from typing import Tuple

from pygraphblas import Matrix
from pygraphblas.binaryop import BinaryOp
from pygraphblas.semiring import Semiring
from pygraphblas.types import Type

from cfpq_matrix.optimized_matrix import OptimizedMatrix, MatrixFormat
from cfpq_matrix.subtractable_semiring import SubOp


class MatrixToOptimizedAdapter(OptimizedMatrix):

    def __init__(self, base: Matrix):
        assert isinstance(base, Matrix)
        self.base = base

    @property
    def nvals(self) -> int:
        return self.base.nvals

    @property
    def shape(self) -> Tuple[int, int]:
        return self.base.shape

    @property
    def format(self) -> MatrixFormat:
        return self.base.format

    @property
    def dtype(self) -> Type:
        return self.base.type

    def to_unoptimized(self) -> Matrix:
        return self.base

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        return (
            other.mxm(self.base, op)
            if swap_operands
            else self.base.mxm(other, op)
        )

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        return op(other, self.base)

    def iadd(self, other: Matrix, op: BinaryOp):
        self.base.eadd(other, add_op=op, out=self.base)

    def optimize_similarly(self, other: Matrix) -> OptimizedMatrix:
        return MatrixToOptimizedAdapter(other)

    def __sizeof__(self):
        return self.base.__sizeof__()
