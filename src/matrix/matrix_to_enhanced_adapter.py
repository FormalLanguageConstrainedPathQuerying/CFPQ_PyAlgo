import gc
from typing import Tuple

import graphblas
from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix

from src.matrix.enhanced_matrix import EnhancedMatrix, MatrixFormat


class MatrixToEnhancedAdapter(EnhancedMatrix):

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
        return self.base.ss.config["format"]

    @property
    def dtype(self) -> DataType:
        return self.base.dtype

    def to_matrix(self) -> Matrix:
        return self.base

    def mxm(self, other: Matrix, swap_operands: bool = False, *args, **kwargs) -> Matrix:
        return (
            other.mxm(self.base, *args, **kwargs)
            if swap_operands
            else self.base.mxm(other, *args, **kwargs)
        ).new(self.dtype)

    def r_complimentary_mask(self, other: Matrix) -> Matrix:
        zero = Matrix(self.base.dtype, nrows=self.base.nrows, ncols=self.base.ncols)
        zero.ss.config["format"] = self.format
        res = Matrix(self.base.dtype, nrows=self.base.nrows, ncols=self.base.ncols)
        res.ss.config["format"] = self.format
        res(~self.base.S) << other.ewise_add(zero, op=graphblas.monoid.any)
        return res

    def iadd(self, other: Matrix):
        # FIXME bool specific code
        self.base << self.base.ewise_add(other, op=graphblas.monoid.any)

    def enhance_similarly(self, base: Matrix) -> EnhancedMatrix:
        return MatrixToEnhancedAdapter(base)

    def __sizeof__(self):
        return self.base.__sizeof__()
