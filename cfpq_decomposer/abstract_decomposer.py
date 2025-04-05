from abc import ABC, abstractmethod

import graphblas
from graphblas.core.dtypes import BOOL
from graphblas.core.matrix import Matrix

from cfpq_decomposer.constants import MAX_SIZE_RATIO, MIN_REDUCTION_RATIO
from cfpq_decomposer.decomposer import Decomposer
from cfpq_matrix.matrix_utils import stack


class AbstractDecomposer(Decomposer, ABC):
    @abstractmethod
    def row_based_decompose(self, matrix: Matrix) -> tuple[Matrix, Matrix]:
        pass

    def column_based_decompose(self, matrix: Matrix):
        left_transposed, right_transposed = self.row_based_decompose(matrix.T.new())
        return right_transposed.T.new(), left_transposed.T.new()

    def decompose(self, matrix: Matrix):
        accumulated_LEFT = []
        accumulated_RIGHT = []
        iteration = 0

        init_nvals = matrix.nvals
        if init_nvals == 0:
            return Matrix(matrix.dtype, matrix.nrows, 0), Matrix(matrix.dtype, 0, matrix.ncols)

        while True:
            iteration += 1
            nvals_before = matrix.nvals

            LEFT1, RIGHT1 = self.row_based_decompose(matrix)

            if LEFT1.nvals != 0:
                matrix = matrix.dup(mask=~LEFT1.mxm(RIGHT1, op=graphblas.semiring.any_pair).new(dtype=BOOL).S)

            LEFT2, RIGHT2 = self.column_based_decompose(matrix)

            if LEFT2.nvals != 0:
                matrix = matrix.dup(mask=~LEFT2.mxm(RIGHT2, op=graphblas.semiring.any_pair).new(dtype=BOOL).S)

            nvals_LEFT_RIGHT = LEFT1.nvals + RIGHT1.nvals + LEFT2.nvals + RIGHT2.nvals

            nvals_after = matrix.nvals
            delta_M = nvals_before - nvals_after

            reduction_ratio = delta_M / nvals_before if nvals_before > 0 else 0
            size_ratio = nvals_LEFT_RIGHT / delta_M if delta_M > 0 else float('inf')

            accumulated_LEFT.extend([LEFT1, LEFT2])
            accumulated_RIGHT.extend([RIGHT1, RIGHT2])

            if reduction_ratio < MIN_REDUCTION_RATIO or size_ratio > MAX_SIZE_RATIO:
                break

            if matrix.nvals == 0:
                break

        if not accumulated_LEFT or not accumulated_RIGHT:
            return Matrix(BOOL, nrows=matrix.nrows, ncols=0), Matrix(BOOL, nrows=0, ncols=matrix.ncols)

        LEFT = stack([accumulated_LEFT])
        RIGHT = stack([[RIGHT] for RIGHT in accumulated_RIGHT])

        return LEFT, RIGHT
