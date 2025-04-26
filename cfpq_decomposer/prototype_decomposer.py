from collections import defaultdict
import random

from graphblas.binary import plus
from graphblas.core.dtypes import BOOL, INT32
from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector

from cfpq_decomposer.abstract_decomposer import AbstractDecomposer
from cfpq_decomposer.constants import HASH_PRIME_MODULUS, HASH_FUNCTIONS_COUNT, PROTOTYPE_MIN_LSH_BUCKET_SIZE, \
    PROTOTYPE_OUTLIER_THRESHOLD, PROTOTYPE_MIN_VALUES_PER_ROW


class PrototypeDecomposer(AbstractDecomposer):
    def row_based_decompose(self, input_matrix: Matrix):
        number_of_rows, number_of_columns = input_matrix.shape
        row_indices, column_indices, _ = input_matrix.to_coo()

        row_to_column_sets = defaultdict(set)
        for row_index, column_index in zip(row_indices, column_indices):
            row_to_column_sets[row_index].add(column_index)

        hash_coefficients_and_offsets = []
        for _ in range(HASH_FUNCTIONS_COUNT):
            coefficient = random.randint(1, HASH_PRIME_MODULUS - 1)
            offset = random.randint(0, HASH_PRIME_MODULUS - 1)
            hash_coefficients_and_offsets.append((coefficient, offset))

        row_to_minhash_signature = {}
        for row_index, column_set in row_to_column_sets.items():
            if len(column_set) < PROTOTYPE_MIN_VALUES_PER_ROW:
                continue
            signature = []
            for coefficient, offset in hash_coefficients_and_offsets:
                min_hash = min((coefficient * col + offset) % HASH_PRIME_MODULUS for col in column_set)
                signature.append(min_hash)
            row_to_minhash_signature[row_index] = tuple(signature)

        row_to_master_hash = {
            row_index: hash(signature)
            for row_index, signature in row_to_minhash_signature.items()
        }

        master_hash_to_rows = defaultdict(list)
        for row_index, master_hash in row_to_master_hash.items():
            master_hash_to_rows[master_hash].append(row_index)

        buckets_with_enough_rows = {
            master_hash: rows
            for master_hash, rows in master_hash_to_rows.items()
            if len(rows) >= PROTOTYPE_MIN_LSH_BUCKET_SIZE
        }

        left_factor_column_vectors = []
        right_factor_row_signatures = []

        for master_hash, bucket_row_indices in buckets_with_enough_rows.items():
            bucket_size = len(bucket_row_indices)
            bucket_submatrix = input_matrix[bucket_row_indices, :].new()
            column_sums = bucket_submatrix.dup(dtype=INT32).reduce_columnwise(plus).new()

            first_threshold = int((1 - PROTOTYPE_OUTLIER_THRESHOLD) * bucket_size)
            frequent_columns_after_first_filter = column_sums.select('>=', first_threshold).new()
            if frequent_columns_after_first_filter.nvals == 0:
                continue

            frequent_column_indices = set(frequent_columns_after_first_filter.to_coo()[0])
            first_filtered_rows = [
                row_index
                for row_index in bucket_row_indices
                if frequent_column_indices <= row_to_column_sets[row_index]
            ]
            if not first_filtered_rows:
                continue

            filtered_submatrix = input_matrix[first_filtered_rows, :].new()
            filtered_column_sums = filtered_submatrix.dup(dtype=INT32).reduce_columnwise(plus)

            second_threshold = int((1 - PROTOTYPE_OUTLIER_THRESHOLD) * len(first_filtered_rows))
            frequent_columns_after_second_filter = filtered_column_sums.select('>=', second_threshold).new()
            if frequent_columns_after_second_filter.nvals == 0:
                continue

            frequent_filtered_column_indices = set(frequent_columns_after_second_filter.to_coo()[0])
            second_filtered_rows = [
                row_index
                for row_index in first_filtered_rows
                if frequent_filtered_column_indices <= row_to_column_sets[row_index]
            ]
            if len(second_filtered_rows) < PROTOTYPE_MIN_LSH_BUCKET_SIZE:
                continue

            right_factor_row_signatures.append(frequent_columns_after_second_filter)

            core_membership_vector = Vector(BOOL, size=number_of_rows)
            for core_row in second_filtered_rows:
                core_membership_vector[core_row] = True
            left_factor_column_vectors.append(core_membership_vector)

        bucket_count = len(left_factor_column_vectors)
        if bucket_count == 0:
            return Matrix(input_matrix.dtype, number_of_rows, 0), \
                   Matrix(input_matrix.dtype, 0, number_of_columns)

        left_factor = Matrix(bool, number_of_rows, bucket_count)
        for idx, column_vector in enumerate(left_factor_column_vectors):
            left_factor[:, idx] = column_vector

        right_factor = Matrix(bool, bucket_count, number_of_columns)
        for idx, row_signature in enumerate(right_factor_row_signatures):
            right_factor[idx, :] = row_signature

        return left_factor, right_factor
