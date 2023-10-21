from graphblas.core.matrix import Matrix

from src.matrix.abstract_enhanced_matrix_decorator import AbstractEnhancedMatrixDecorator
from src.matrix.enhanced_matrix import EnhancedMatrix


class ShortCircuitingForEmptyMatrix(AbstractEnhancedMatrixDecorator):
    def __init__(self, base: EnhancedMatrix):
        self._base = base

    @property
    def base(self) -> EnhancedMatrix:
        return self._base

    def mxm(self, other: Matrix, *args, **kwargs) -> Matrix:
        if self.nvals == 0 or other.nvals == 0:
            assert self.shape[1] == other.shape[0]
            return Matrix(self.dtype, self.shape[0], other.shape[1])
        return self.base.mxm(other, *args, **kwargs)

    def r_complimentary_mask(self, other: Matrix) -> Matrix:
        if self.nvals == 0 or other.nvals == 0:
            return other
        return self.base.r_complimentary_mask(other)

    def iadd(self, other: Matrix):
        if other.nvals != 0:
            self.base.iadd(other)

    def enhance_similarly(self, base: Matrix) -> "EnhancedMatrix":
        return ShortCircuitingForEmptyMatrix(self.base.enhance_similarly(base))
