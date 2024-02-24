from graphblas.core.matrix import Matrix
from graphblas.core.operator import Semiring, Monoid

from src.matrix.abstract_optimized_matrix_decorator import AbstractOptimizedMatrixDecorator
from src.matrix.optimized_matrix import OptimizedMatrix
from src.utils.subtractable_semiring import SubOp


class EmptyOptimizedMatrix(AbstractOptimizedMatrixDecorator):
    def __init__(self, base: OptimizedMatrix):
        self._base = base

    @property
    def base(self) -> OptimizedMatrix:
        return self._base

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        if self.nvals == 0 or other.nvals == 0:
            if swap_operands:
                assert self.shape[0] == other.shape[1]
                return Matrix(self.dtype, self.shape[1], other.shape[0])
            else:
                assert self.shape[1] == other.shape[0]
                return Matrix(self.dtype, self.shape[0], other.shape[1])
        return self.base.mxm(other, op, swap_operands)

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        if self.nvals == 0 or other.nvals == 0:
            return other
        return self.base.rsub(other, op)

    def iadd(self, other: Matrix, op: Monoid):
        if other.nvals != 0:
            self.base.iadd(other, op=op)

    def optimize_similarly(self, other: Matrix) -> "OptimizedMatrix":
        return EmptyOptimizedMatrix(self.base.optimize_similarly(other))

    def __sizeof__(self):
        return self.base.__sizeof__()
