from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional

import random

from graphblas.binary import plus
from graphblas.core.dtypes import BOOL, INT32
from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector

from cfpq_decomposer.abstract_decomposer import AbstractDecomposer
from cfpq_decomposer.constants import (
    HASH_PRIME_MODULUS,
    HASH_FUNCTIONS_COUNT,
    PROTOTYPE_MIN_LSH_BUCKET_SIZE,
    PROTOTYPE_OUTLIER_THRESHOLD,
    PROTOTYPE_MIN_VALUES_PER_ROW,
)


@dataclass
class BucketFactor:
    membership_vector: Vector
    column_signature: Vector


class PrototypeDecomposer(AbstractDecomposer):
    def row_based_decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        row_to_column_sets = self._extract_row_to_column_sets(matrix)
        row_minhash_signatures = self._compute_row_minhash_signatures(row_to_column_sets)
        master_hash_to_rows = self._group_rows_by_master_hash(row_minhash_signatures)
        bucket_factors = self._build_bucket_factors(master_hash_to_rows, row_to_column_sets, matrix)
        return self._build_factor_matrices(bucket_factors, matrix)

    @staticmethod
    def _extract_row_to_column_sets(matrix: Matrix) -> Dict[int, Set[int]]:
        row_to_column_sets: Dict[int, Set[int]] = defaultdict(set)
        rows, cols, _ = matrix.to_coo()
        for r, c in zip(rows, cols):
            row_to_column_sets[r].add(c)
        return row_to_column_sets

    @staticmethod
    def _generate_hash_coefficients_and_offsets() -> List[Tuple[int, int]]:
        coefficients_and_offsets: List[Tuple[int, int]] = []
        for _ in range(HASH_FUNCTIONS_COUNT):
            coefficient = random.randint(1, HASH_PRIME_MODULUS - 1)
            offset = random.randint(0, HASH_PRIME_MODULUS - 1)
            coefficients_and_offsets.append((coefficient, offset))
        return coefficients_and_offsets

    @classmethod
    def _compute_row_minhash_signatures(
        cls,
        row_to_column_sets: Dict[int, Set[int]],
    ) -> Dict[int, Tuple[int, ...]]:
        hash_params = cls._generate_hash_coefficients_and_offsets()
        row_minhash_signatures: Dict[int, Tuple[int, ...]] = {}
        for row_index, column_set in row_to_column_sets.items():
            if len(column_set) < PROTOTYPE_MIN_VALUES_PER_ROW:
                continue
            signature = tuple(
                min((coef * col + off) % HASH_PRIME_MODULUS for col in column_set)
                for coef, off in hash_params
            )
            row_minhash_signatures[row_index] = signature
        return row_minhash_signatures

    @staticmethod
    def _group_rows_by_master_hash(
        row_minhash_signatures: Dict[int, Tuple[int, ...]],
    ) -> Dict[int, List[int]]:
        master_hash_to_rows: Dict[int, List[int]] = defaultdict(list)
        for row_index, signature in row_minhash_signatures.items():
            master_hash_to_rows[hash(signature)].append(row_index)
        return {
            master_hash: rows
            for master_hash, rows in master_hash_to_rows.items()
            if len(rows) >= PROTOTYPE_MIN_LSH_BUCKET_SIZE
        }

    @staticmethod
    def _build_bucket_factors(
        master_hash_to_rows: Dict[int, List[int]],
        row_to_column_sets: Dict[int, Set[int]],
        matrix: Matrix,
    ) -> List[BucketFactor]:
        bucket_factors: List[BucketFactor] = []
        for bucket_rows in master_hash_to_rows.values():
            factor = PrototypeDecomposer._build_bucket_factor(bucket_rows, row_to_column_sets, matrix)
            if factor:
                bucket_factors.append(factor)
        return bucket_factors

    @staticmethod
    def _filter_rows_by_frequency(
        candidate_rows: List[int],
        row_to_column_sets: Dict[int, Set[int]],
        matrix: Matrix,
    ) -> Tuple[Optional[Vector], List[int]]:
        submatrix = matrix[candidate_rows, :].new()
        column_sums = submatrix.dup(dtype=INT32).reduce_columnwise(plus).new()
        threshold = int((1 - PROTOTYPE_OUTLIER_THRESHOLD) * len(candidate_rows))
        frequency_signature = column_sums.select('>=', threshold).new()
        if frequency_signature.nvals == 0:
            return None, []
        frequent_column_indices = set(frequency_signature.to_coo()[0])
        surviving_rows = [
            r
            for r in candidate_rows
            if frequent_column_indices <= row_to_column_sets[r]
        ]
        return frequency_signature, surviving_rows

    @staticmethod
    def _build_bucket_factor(
        bucket_rows: List[int],
        row_to_column_sets: Dict[int, Set[int]],
        matrix: Matrix,
    ) -> Optional[BucketFactor]:
        num_rows, _ = matrix.shape

        first_round_signature, rows_after_first_filter = PrototypeDecomposer._filter_rows_by_frequency(
            bucket_rows, row_to_column_sets, matrix
        )
        if first_round_signature is None or len(rows_after_first_filter) < PROTOTYPE_MIN_LSH_BUCKET_SIZE:
            return None

        second_round_signature, rows_after_second_filter = PrototypeDecomposer._filter_rows_by_frequency(
            rows_after_first_filter, row_to_column_sets, matrix
        )
        if second_round_signature is None or len(rows_after_second_filter) < PROTOTYPE_MIN_LSH_BUCKET_SIZE:
            return None

        membership_vector = Vector(BOOL, size=num_rows)
        for row_index in rows_after_second_filter:
            membership_vector[row_index] = True
        return BucketFactor(
            membership_vector=membership_vector,
            column_signature=second_round_signature
        )

    @staticmethod
    def _build_factor_matrices(
        bucket_factors: List[BucketFactor],
        matrix: Matrix,
    ) -> Tuple[Matrix, Matrix]:
        num_rows, num_cols = matrix.shape
        num_buckets = len(bucket_factors)
        if num_buckets == 0:
            return Matrix(BOOL, num_rows, 0), Matrix(BOOL, 0, num_cols)
        left_factor = Matrix(BOOL, num_rows, num_buckets)
        right_factor = Matrix(BOOL, num_buckets, num_cols)
        for idx, factor in enumerate(bucket_factors):
            left_factor[:, idx] = factor.membership_vector
            right_factor[idx, :] = factor.column_signature
        return left_factor, right_factor
