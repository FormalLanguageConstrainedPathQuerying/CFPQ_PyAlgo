from dataclasses import dataclass
from typing import Tuple, Any

import numpy as np
import numpy.typing as npt
from graphblas import semiring
from graphblas.core.dtypes import INT64, BOOL, INT32
from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector

from cfpq_decomposer.abstract_decomposer import AbstractDecomposer
from cfpq_decomposer.constants import HASH_PRIME_MODULUS, HASH_FUNCTIONS_COUNT, MIN_LSH_BUCKET_SIZE, SMALL_BUCKET_ID
from cfpq_matrix.matrix_utils import drop_zeros_inplace


@dataclass
class BuildLeftFactorResult:
    left_factor: Matrix
    bucket_sizes: npt.NDArray[np.int64]


@dataclass
class RowGroupingResult:
    row_to_bucket: npt.NDArray[np.int64]
    bucket_sizes: npt.NDArray[np.int64]

    @property
    def num_buckets(self):
        return self.bucket_sizes.size

    @property
    def rows_in_buckets(self):
        return self.row_to_bucket != SMALL_BUCKET_ID


class HighPerformanceDecomposer(AbstractDecomposer):
    def row_based_decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        build_left_factor_result = self._build_left_factor(matrix)
        right_factor = self._build_right_factor(matrix, build_left_factor_result)
        return build_left_factor_result.left_factor, right_factor

    @staticmethod
    def _build_left_factor(matrix: Matrix) -> BuildLeftFactorResult:
        num_rows, num_cols = matrix.shape

        row_grouping_result = HighPerformanceDecomposer._group_rows_to_buckets(matrix)

        row_to_bucket = row_grouping_result.row_to_bucket
        bucket_sizes = row_grouping_result.bucket_sizes
        rows_in_buckets = row_grouping_result.rows_in_buckets

        left_factor = Matrix.from_coo(
            rows=np.nonzero(rows_in_buckets)[0].astype(np.uint64),
            columns=row_to_bucket[rows_in_buckets].astype(np.uint64),
            values=np.ones(bucket_sizes.sum(), dtype=bool),
            dtype=BOOL,
            nrows=num_rows,
            ncols=row_grouping_result.num_buckets
        )
        return BuildLeftFactorResult(left_factor, bucket_sizes)

    @staticmethod
    def _group_rows_to_buckets(matrix: Matrix) -> RowGroupingResult:
        row_hashes = HighPerformanceDecomposer._compute_row_hashes(matrix)
        return HighPerformanceDecomposer._group_row_hashes_to_buckets(row_hashes)

    @staticmethod
    def _compute_row_hashes(matrix: Matrix) -> npt.NDArray[Any]:
        row_signatures_matrix = HighPerformanceDecomposer._compute_row_signatures_matrix(matrix)
        hash_weights = np.random.default_rng().integers(
            low=1,
            high=np.iinfo(np.int64).max,
            size=HASH_FUNCTIONS_COUNT,
            dtype=np.int64
        )
        row_hashes = row_signatures_matrix.to_dense(fill_value=0) @ hash_weights
        return row_hashes

    @staticmethod
    def _compute_row_signatures_matrix(matrix: Matrix) -> Matrix:
        num_rows, num_cols = matrix.shape
        hash_coefficients = np.random.randint(1, HASH_PRIME_MODULUS, size=HASH_FUNCTIONS_COUNT, dtype=np.int64)
        hash_offsets = np.random.randint(0, HASH_PRIME_MODULUS, size=HASH_FUNCTIONS_COUNT, dtype=np.int64)
        column_indices = np.arange(num_cols, dtype=np.int64)
        hash_matrix = Matrix.from_dense(
            (column_indices[:, None] * hash_coefficients[None, :] + hash_offsets[None, :]) % HASH_PRIME_MODULUS
        )
        row_signatures_matrix = Matrix(INT64, num_rows, HASH_FUNCTIONS_COUNT)
        row_signatures_matrix << semiring.min_second(matrix @ hash_matrix)
        return row_signatures_matrix

    @staticmethod
    def _group_row_hashes_to_buckets(row_hashes: npt.NDArray[Any]) -> RowGroupingResult:

        _, row_to_bucket, new_bucket_sizes = np.unique(
            row_hashes, return_inverse=True, return_counts=True
        )
        bucket_validity = new_bucket_sizes >= MIN_LSH_BUCKET_SIZE
        valid_bucket_ids = np.nonzero(bucket_validity)[0]

        old_bucket_id_to_new_bucket_id = np.full_like(new_bucket_sizes, SMALL_BUCKET_ID, dtype=np.int64)
        old_bucket_id_to_new_bucket_id[valid_bucket_ids] = np.arange(valid_bucket_ids.size, dtype=np.int64)

        new_row_to_bucket = np.where(
            bucket_validity[row_to_bucket],
            old_bucket_id_to_new_bucket_id[row_to_bucket],
            SMALL_BUCKET_ID,
        )
        new_bucket_sizes = new_bucket_sizes[valid_bucket_ids]

        return RowGroupingResult(row_to_bucket=new_row_to_bucket, bucket_sizes=new_bucket_sizes)

    @staticmethod
    def _build_right_factor(matrix: Matrix, build_left_factor_result: BuildLeftFactorResult) -> Matrix:
        """
        This function essentially computes the value of
        `semiring.and_implies(build_left_factor_result.left_factor @ matrix).new()`.

        However, `semiring.and_implies` is not a valid semiring,
        so we have to simulate it by performing multiple operations.
        """
        left_factor = build_left_factor_result.left_factor
        bucket_sizes = build_left_factor_result.bucket_sizes

        num_rows, num_cols = matrix.shape
        num_valid_buckets = bucket_sizes.size

        occurrence_matrix = Matrix(INT32, num_valid_buckets, num_cols)
        occurrence_matrix << semiring.plus_times(left_factor.dup(dtype=INT32).T @ matrix.dup(dtype=INT32))

        right_factor = (occurrence_matrix.T == Vector.from_dense(bucket_sizes)).T.new()
        return drop_zeros_inplace(right_factor)
