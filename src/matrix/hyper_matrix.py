from abc import ABC

from graphblas.core.matrix import Matrix

from src.matrix.abstract_enhanced_matrix_decorator import AbstractEnhancedMatrixDecorator
from src.matrix.enhanced_matrix import EnhancedMatrix
from src.matrix.hyper_matrix_space import HyperMatrixSpace, HyperVectorOrientation


class HyperMatrix(AbstractEnhancedMatrixDecorator, ABC):
    def __init__(self, base: EnhancedMatrix, hyper_space: HyperMatrixSpace):
        self._base = base
        self.hyper_space = hyper_space

    @property
    def base(self) -> EnhancedMatrix:
        return self._base

    def enhance_similarly(self, base: Matrix) -> "EnhancedMatrix":
        return self.hyper_space.wrap_enhanced_hyper_matrix(self.base.enhance_similarly(base))


class CellHyperMatrix(HyperMatrix):
    def __init__(self, base: EnhancedMatrix, hyper_space: HyperMatrixSpace):
        assert hyper_space.is_single_cell(base.shape)
        super().__init__(base, hyper_space)

    def mxm(self, other: Matrix, swap_operands: bool = False, *args, **kwargs) -> Matrix:
        if self.hyper_space.is_single_cell(other.shape):
            return self.base.mxm(other, swap_operands=swap_operands, *args, **kwargs)
        else:
            return self.base.mxm(
                self.hyper_space.hyper_rotate(
                    other,
                    HyperVectorOrientation.VERTICAL if swap_operands else HyperVectorOrientation.HORIZONTAL
                ),
                swap_operands=swap_operands,
                *args,
                **kwargs
            )

    def r_complimentary_mask(self, other: Matrix) -> Matrix:
        assert self.hyper_space.is_single_cell(other.shape)
        return self.base.r_complimentary_mask(other)

    def iadd(self, other: Matrix):
        self.base.iadd(other)

    def __sizeof__(self):
        return self.base.__sizeof__()


class VectorHyperMatrix(HyperMatrix):
    def __init__(self, base: EnhancedMatrix, hyper_space: HyperMatrixSpace):
        assert hyper_space.is_hyper_vector(base.shape)
        super().__init__(base, hyper_space)
        self.matrices = {hyper_space.get_hyper_orientation(base.shape): base}

    def _force_init_orientation(self, desired_orientation: HyperVectorOrientation) -> "EnhancedMatrix":
        if desired_orientation not in self.matrices:
            base_matrix = self.hyper_space.hyper_rotate(self.base.to_matrix(), desired_orientation)
            self.matrices[desired_orientation] = self.base.enhance_similarly(base_matrix)
        return self.matrices[desired_orientation]

    def mxm(self, other: Matrix, swap_operands: bool = False, *args, **kwargs) -> Matrix:
        if self.hyper_space.is_single_cell(other.shape):
            return self._force_init_orientation(
                HyperVectorOrientation.HORIZONTAL if swap_operands else HyperVectorOrientation.VERTICAL
            ).mxm(other, swap_operands=swap_operands, *args, **kwargs)
        else:
            return self._force_init_orientation(
                HyperVectorOrientation.VERTICAL if swap_operands else HyperVectorOrientation.HORIZONTAL
            ).mxm(
                self.hyper_space.to_block_diag_matrix(other),
                swap_operands=swap_operands,
                *args,
                **kwargs
            )

    def r_complimentary_mask(self, other: Matrix) -> Matrix:
        if self.hyper_space.get_hyper_orientation(other.shape) not in self.matrices:
            other = self.hyper_space.hyper_rotate(other, self.matrices.keys().__iter__().__next__())
        return self.matrices[self.hyper_space.get_hyper_orientation(other.shape)].r_complimentary_mask(other)

    def iadd(self, other: Matrix):
        for (orientation, m) in self.matrices.items():
            m.iadd(
                self.hyper_space.hyper_rotate(other, orientation)
            )

    def __sizeof__(self):
        return sum(m.__sizeof__() for m in self.matrices.values())
