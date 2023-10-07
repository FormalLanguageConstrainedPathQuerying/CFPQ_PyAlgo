from typing import Tuple

from pygraphblas import Matrix, descriptor

from src.matrix.enhanced_matrix import EnhancedMatrix, MatrixForm


class MatrixToEnhancedAdapter(EnhancedMatrix):

    def __init__(self, base: Matrix):
        self.base = base

    @property
    def nvals(self) -> int:
        return self.base.nvals

    @property
    def shape(self) -> Tuple[int, int]:
        return self.base.shape

    @property
    def format(self) -> MatrixForm:
        return self.base.format

    def to_matrix(self) -> Matrix:
        return self.base

    def mxm(self, other: Matrix, swap_operands: bool = False, *args, **kwargs) -> Matrix:
        return other.mxm(self.base, *args, **kwargs) if swap_operands else self.base.mxm(other, *args, **kwargs)

    def r_complimentary_mask(self, other: Matrix) -> Matrix:
        zero = Matrix.sparse(self.base.type, nrows=self.base.nrows, ncols=self.base.ncols)
        zero.format = self.base.format
        res = Matrix.sparse(self.base.type, nrows=self.base.nrows, ncols=self.base.ncols)
        res.format = self.base.format
        return other.eadd(zero, mask=self.base, desc=descriptor.C, out=res)

    def iadd(self, other: Matrix):
        self.base += other

    def enhance_similarly(self, base: Matrix) -> EnhancedMatrix:
        return MatrixToEnhancedAdapter(base)
