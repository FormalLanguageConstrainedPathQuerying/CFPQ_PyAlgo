from abc import ABC, abstractmethod
from typing import Tuple

import graphblas
from graphblas.core.dtypes import BOOL
from graphblas.core.matrix import Matrix

from cfpq_decomposer.constants import MAX_SIZE_RATIO, MIN_REDUCTION_RATIO
from cfpq_decomposer.decomposer import Decomposer
from cfpq_matrix.matrix_utils import stack


class AbstractDecomposer(Decomposer, ABC):
    @abstractmethod
    def row_based_decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        """
        Decomposes a sparse boolean matrix `matrix` into matrices
        `left`, `right` so that `matrix[i, j] >= (left @ right)[i, j]`
        for all entries.

        Only extracts very trivial row patterns.
        """

    def column_based_decompose(self, matrix: Matrix):
        """
        Decomposes a sparse boolean matrix `matrix` into matrices
        `left`, `right` so that `matrix[i, j] >= (left @ right)[i, j]`
        for all entries.

        Only extracts very trivial column patterns.
        """
        left_transposed, right_transposed = self.row_based_decompose(matrix.T.new())
        return right_transposed.T.new(), left_transposed.T.new()

    def decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        residual = matrix
        if residual.nvals == 0:
            return (
                Matrix(matrix.dtype, matrix.nrows, 0),
                Matrix(matrix.dtype, 0, matrix.ncols),
            )

        left_blocks: list[Matrix] = []
        right_blocks: list[Matrix] = []

        while True:
            nvals_before = residual.nvals

            l1, r1 = self.row_based_decompose(residual)
            if l1.nvals:
                mask = ~l1.mxm(r1, op=graphblas.semiring.any_pair).new(dtype=BOOL).S
                residual = residual.dup(mask=mask)

            l2, r2 = self.column_based_decompose(residual)
            if l2.nvals:
                mask = ~l2.mxm(r2, op=graphblas.semiring.any_pair).new(dtype=BOOL).S
                residual = residual.dup(mask=mask)

            left_blocks.extend([l1, l2])
            right_blocks.extend([r1, r2])

            nvals_after = residual.nvals
            nvals_delta = nvals_before - nvals_after
            reduction_ratio = (nvals_delta / nvals_before) if nvals_before else 0
            size_ratio = ((l1.nvals + r1.nvals + l2.nvals + r2.nvals) / nvals_delta) if nvals_delta else float("inf")

            if reduction_ratio < MIN_REDUCTION_RATIO or size_ratio > MAX_SIZE_RATIO or residual.nvals == 0:
                break

        if not left_blocks:
            return (
                Matrix(matrix.dtype, matrix.nrows, 0),
                Matrix(matrix.dtype, 0, matrix.ncols),
            )

        left = stack([left_blocks])
        right = stack([[block] for block in right_blocks])
        return left, right
