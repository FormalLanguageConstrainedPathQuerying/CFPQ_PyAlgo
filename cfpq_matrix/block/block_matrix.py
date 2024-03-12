from abc import ABC

from graphblas.core.matrix import Matrix
from graphblas.core.operator import Monoid, Semiring

from cfpq_matrix.abstract_optimized_matrix_decorator import AbstractOptimizedMatrixDecorator
from cfpq_matrix.optimized_matrix import OptimizedMatrix
from cfpq_matrix.block.block_matrix_space import BlockMatrixSpace, BlockMatrixOrientation
from cfpq_model.subtractable_semiring import SubOp


class BlockMatrix(AbstractOptimizedMatrixDecorator, ABC):
    def __init__(self, base: OptimizedMatrix, hyper_space: BlockMatrixSpace):
        self._base = base
        self.block_matrix_space = hyper_space

    @property
    def base(self) -> OptimizedMatrix:
        return self._base

    def optimize_similarly(self, other: Matrix) -> "OptimizedMatrix":
        return self.block_matrix_space.automize_block_operations(self.base.optimize_similarly(other))


class CellBlockMatrix(BlockMatrix):
    def __init__(self, base: OptimizedMatrix, block_matrix_space: BlockMatrixSpace):
        assert block_matrix_space.is_single_cell(base.shape)
        super().__init__(base, block_matrix_space)

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        if self.block_matrix_space.is_single_cell(other.shape):
            return self.base.mxm(other, op, swap_operands=swap_operands)
        else:
            return self.base.mxm(
                self.block_matrix_space.hyper_rotate(
                    other,
                    BlockMatrixOrientation.VERTICAL if swap_operands else BlockMatrixOrientation.HORIZONTAL
                ),
                op,
                swap_operands=swap_operands,
            )

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        assert self.block_matrix_space.is_single_cell(other.shape)
        return self.base.rsub(other, op)

    def iadd(self, other: Matrix, op: Monoid):
        self.base.iadd(self.block_matrix_space.reduce_hyper_vector_or_cell(other, op), op)

    def __sizeof__(self):
        return self.base.__sizeof__()


class VectorBlockMatrix(BlockMatrix):
    def __init__(
        self,
        base: OptimizedMatrix,
        block_matrix_space: BlockMatrixSpace,
        discard_base_on_reformat: bool = True,
    ):
        assert block_matrix_space.is_hyper_vector(base.shape)
        super().__init__(base, block_matrix_space)
        self.matrices = {block_matrix_space.get_block_matrix_orientation(base.shape): base}
        self.discard_base_on_reformat = discard_base_on_reformat

    def _force_init_orientation(self, desired_orientation: BlockMatrixOrientation) -> "OptimizedMatrix":
        if desired_orientation not in self.matrices:
            rotated_matrix = self.block_matrix_space.hyper_rotate(self.base.to_unoptimized(), desired_orientation)
            self.matrices[desired_orientation] = self.base.optimize_similarly(rotated_matrix)
            if self.discard_base_on_reformat:
                del self.matrices[self.block_matrix_space.get_block_matrix_orientation(self.base.shape)]
                self._base = self.matrices[desired_orientation]
        self.discard_base_on_reformat = False
        return self.matrices[desired_orientation]

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        if self.block_matrix_space.is_single_cell(other.shape):
            return self._force_init_orientation(
                BlockMatrixOrientation.HORIZONTAL if swap_operands else BlockMatrixOrientation.VERTICAL
            ).mxm(other, op, swap_operands=swap_operands)
        else:
            return self._force_init_orientation(
                BlockMatrixOrientation.VERTICAL if swap_operands else BlockMatrixOrientation.HORIZONTAL
            ).mxm(self.block_matrix_space.to_block_diag_matrix(other), op, swap_operands=swap_operands)

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        if self.block_matrix_space.get_block_matrix_orientation(other.shape) not in self.matrices:
            other = self.block_matrix_space.hyper_rotate(other, self.matrices.keys().__iter__().__next__())
        return self.matrices[self.block_matrix_space.get_block_matrix_orientation(other.shape)].rsub(other, op)

    def iadd(self, other: Matrix, op: Monoid):
        if self.block_matrix_space.is_single_cell(other.shape):
            other = self.block_matrix_space.repeat_into_hyper_column(other)
        for (orientation, m) in self.matrices.items():
            m.iadd(
                self.block_matrix_space.hyper_rotate(other, orientation),
                op=op
            )

    def __sizeof__(self):
        return sum(m.__sizeof__() for m in self.matrices.values())
