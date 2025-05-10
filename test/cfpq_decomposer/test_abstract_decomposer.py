from abc import ABC, abstractmethod
from typing import Tuple

import graphblas
import pytest
from graphblas.core.dtypes import BOOL
from graphblas.core.matrix import Matrix

from cfpq_decomposer.decomposer import Decomposer
from test.cfpq_decomposer.synthetic_data import (
    similar_rows_matrix,
    multiple_patterns_matrix,
    double_threshold_matrix,
    similar_columns_matrix,
    random_matrix_with_patterns, MIN_COMPRESSION_FACTORS
)

class AbstractDecomposerTest(ABC):
    @abstractmethod
    def create_decomposer(self) -> Decomposer:
        pass

    def decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        return self.create_decomposer().decompose(matrix)

    @pytest.mark.CI
    @pytest.mark.parametrize("matrix_fn,key", [
        pytest.param(similar_rows_matrix, "similar_rows", id="similar_rows"),
        pytest.param(multiple_patterns_matrix, "multiple_patterns", id="multiple_patterns"),
        pytest.param(double_threshold_matrix, "double_threshold", id="double_threshold"),
        pytest.param(similar_columns_matrix, "similar_columns", id="similar_columns"),
        pytest.param(random_matrix_with_patterns, "random_patterns", id="random_patterns"),
    ])
    def test_decomposition(self, matrix_fn, key):
        matrix = matrix_fn()
        left, right = self.decompose(matrix)
        left_right = left.mxm(right, op=graphblas.semiring.any_pair).new(dtype=BOOL)
        assert left_right.dup(mask=~matrix.S).nvals == 0
        remainder = matrix.dup(mask=~left_right.S).nvals
        compression_factor = matrix.nvals / (left.nvals + right.nvals + remainder)
        print(f"Compression factor for {key} is {compression_factor}")
        assert compression_factor > MIN_COMPRESSION_FACTORS[key]
