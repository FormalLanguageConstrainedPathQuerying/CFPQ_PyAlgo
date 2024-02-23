from abc import ABC
from typing import Dict

from graphblas.core.matrix import Matrix
from graphblas.core.operator import Monoid, Semiring

from src.matrix.abstract_optimized_matrix_decorator import AbstractOptimizedMatrixDecorator
from src.matrix.optimized_matrix import OptimizedMatrix
from src.matrix.hyper_matrix_space import HyperMatrixSpace, HyperVectorOrientation
from src.utils.subtractable_semiring import SubOp


class HyperMatrix(AbstractOptimizedMatrixDecorator, ABC):
    def __init__(self, base: OptimizedMatrix, hyper_space: HyperMatrixSpace):
        self._base = base
        self.hyper_space = hyper_space

    @property
    def base(self) -> OptimizedMatrix:
        return self._base

    def optimize_similarly(self, other: Matrix) -> "OptimizedMatrix":
        return self.hyper_space.wrap_enhanced_hyper_matrix(self.base.optimize_similarly(other))


class CellHyperMatrix(HyperMatrix):
    def __init__(self, base: OptimizedMatrix, hyper_space: HyperMatrixSpace):
        assert hyper_space.is_single_cell(base.shape)
        super().__init__(base, hyper_space)

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        if self.hyper_space.is_single_cell(other.shape):
            return self.base.mxm(other, op, swap_operands=swap_operands)
        else:
            return self.base.mxm(
                self.hyper_space.hyper_rotate(
                    other,
                    HyperVectorOrientation.VERTICAL if swap_operands else HyperVectorOrientation.HORIZONTAL
                ),
                op,
                swap_operands=swap_operands,
            )

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        assert self.hyper_space.is_single_cell(other.shape)
        return self.base.rsub(other, op)

    def iadd(self, other: Matrix, op: Monoid):
        self.base.iadd(self.hyper_space.reduce_hyper_vector_or_cell(other), op)

    def __sizeof__(self):
        return self.base.__sizeof__()


class VectorHyperMatrix(HyperMatrix):
    def __init__(
        self,
        base: OptimizedMatrix,
        hyper_space: HyperMatrixSpace,
        discard_base_on_reformat: bool = True,
    ):
        assert hyper_space.is_hyper_vector(base.shape)
        super().__init__(base, hyper_space)
        self.matrices = {hyper_space.get_hyper_orientation(base.shape): base}
        self.discard_base_on_reformat = discard_base_on_reformat

    def _force_init_orientation(self, desired_orientation: HyperVectorOrientation) -> "OptimizedMatrix":
        if desired_orientation not in self.matrices:
            base_matrix = self.hyper_space.hyper_rotate(self.base.to_unoptimized(), desired_orientation)
            self.matrices[desired_orientation] = self.base.optimize_similarly(base_matrix)
            if self.discard_base_on_reformat:
                del self.matrices[self.hyper_space.get_hyper_orientation(self.base.shape)]
                self._base = self.matrices[desired_orientation]
        self.discard_base_on_reformat = False
        return self.matrices[desired_orientation]

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        if self.hyper_space.is_single_cell(other.shape):
            return self._force_init_orientation(
                HyperVectorOrientation.HORIZONTAL if swap_operands else HyperVectorOrientation.VERTICAL
            ).mxm(other, op, swap_operands=swap_operands)
        else:
            return self._force_init_orientation(
                HyperVectorOrientation.VERTICAL if swap_operands else HyperVectorOrientation.HORIZONTAL
            ).mxm(self.hyper_space.to_block_diag_matrix(other), op, swap_operands=swap_operands)

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        if self.hyper_space.get_hyper_orientation(other.shape) not in self.matrices:
            other = self.hyper_space.hyper_rotate(other, self.matrices.keys().__iter__().__next__())
        return self.matrices[self.hyper_space.get_hyper_orientation(other.shape)].rsub(other, op)

    def iadd(self, other: Matrix, op: Monoid):
        if self.hyper_space.is_single_cell(other.shape):
            other = self.hyper_space.repeat_into_hyper_column(other)
        for (orientation, m) in self.matrices.items():
            m.iadd(
                self.hyper_space.hyper_rotate(other, orientation),
                op=op
            )

    def __sizeof__(self):
        return sum(m.__sizeof__() for m in self.matrices.values())
