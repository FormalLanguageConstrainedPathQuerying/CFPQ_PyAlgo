from typing import Tuple

from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix
from graphblas.core.operator import Monoid, Semiring

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
        return self.base.ss.config["format"]

    @property
    def dtype(self) -> DataType:
        return self.base.dtype

    def to_mask(self) -> Matrix:
        return self.base
        
    def to_unoptimized(self) -> Matrix:
        return self.base

    def mxm(self, other: Matrix, op: Semiring, mask: Matrix, swap_operands: bool = False) -> Matrix:
        #   return (
        #    other.mxm(self.base, op)
        #    if swap_operands
        #    else self.base.mxm(other, op)
        #).new(self.dtype)
        if swap_operands:
            if not mask is None:
                #print("Mask applied, swap operands") 
                #result = Matrix(self.dtype,nrows=other.shape[0],ncols=self.shape[1])
                #mask_t = Matrix(mask.dtype, ncols=mask.ncols, nrows=mask.nrows)
                #mask_t << mask.T 
                #result(~mask) << other.mxm(self.base, op)
                #result(~mask) << other.mxm(self.base, op).new(self.dtype)
                #return result
                return other.mxm(self.base, op).new(self.dtype)
            else: return other.mxm(self.base, op).new(self.dtype)
        else:
            if not mask is None:
                print("Mask applied")
                result = Matrix(self.dtype,nrows=self.shape[0],ncols=other.shape[1])
                #result(~mask) << self.base.mxm(other, op)
                result(~mask) << self.base.mxm(other, op).new(self.dtype)
                return result
                #return self.base.mxm(other, op).new(self.dtype)
            else: return self.base.mxm(other, op).new(self.dtype)
        

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        return op(other, self.base)

    def iadd(self, other: Matrix, op: Monoid):
        self.base << self.base.ewise_add(other, op=op)

    def optimize_similarly(self, other: Matrix) -> OptimizedMatrix:
        return MatrixToOptimizedAdapter(other)

    def __sizeof__(self):
        return self.base.__sizeof__()
