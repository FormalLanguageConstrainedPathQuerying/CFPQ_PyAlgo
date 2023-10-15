from abc import ABC
from typing import Callable, Optional, Tuple

from pygraphblas import Matrix

from src.matrix.abstract_enhanced_matrix_decorator import AbstractEnhancedMatrixDecorator
from src.matrix.enhanced_matrix import EnhancedMatrix
from src.matrix.hyper_matrix_space import HyperMatrixSpace, HyperVectorOrientation


# class HyperMatrix(EnhancedMatrix):
#     def __init__(self, hyper_size: int, base_factory: Callable[[Optional[Matrix]], EnhancedMatrix]):
#         self.hyper_size = hyper_size
#         self.base_factory = base_factory
#         self.base = base_factory(None)
#         self.n = min(self.base.ncols, self.base.nrows)
#         if self.base.nrows == self.base.ncols:
#             self.cell = self.base
#         else:
#             self.cell = None
#             if self.base.nrows == self.n * hyper_size and self.base.ncols == self.n:
#                 self.column = self.base
#                 self.row = None
#             elif self.base.nrows == self.n and self.base.ncols == self.n * hyper_size:
#                 self.row = self.base
#                 self.column = None
#             else:
#                 raise RuntimeError(
#                     f"Either hyper_size is incorrect or base matrix cell is not a square which is not supported, "
#                     f"hyper_size: {hyper_size}, base.shape: {self.base.ncols}, {self.base.nrows}"
#                 )
#         self.utils = HyperMatrixUtils(self.n, hyper_size)
#
#     @property
#     def nvals(self) -> int:
#         return self.base.nvals
#
#     @property
#     def nrows(self) -> int:
#         return self.n
#
#     @property
#     def ncols(self) -> int:
#         return self.n
#
#     @property
#     def format(self) -> MatrixFormat:
#         return self.base.format
#
#     def to_matrix(self) -> Matrix:
#         if self.cell is not None:
#             return self.cell
#         elif self.column is not None:
#             return self.utils.reduce_hyper_column(self.column.to_matrix())
#         else:
#             assert self.row is not None
#             return self.utils.reduce_hyper_row(self.row.to_matrix())
#
#     def _force_init_row(self) -> EnhancedMatrix:
#         if self.row is None:
#             print("_force_init_row")  # TODO remove debug print
#             assert self.column is not None
#             self.row = self.base_factory(self.utils.hyper_column_to_hyper_row(self.column.to_matrix()))
#         return self.row
#
#     def _force_init_column(self) -> EnhancedMatrix:
#         if self.column is None:
#             print("_force_init_column")  # TODO remove debug print
#             assert self.row is not None
#             self.column = self.base_factory(self.utils.hyper_row_to_hyper_column(self.row.to_matrix()))
#         return self.column
#
#     def mxm(self, other: Matrix, *args, **kwargs) -> Matrix:
#         if self.cell is not None:
#             if self.utils.is_single_cell(other):
#                 return self.cell.mxm(other, *args, **kwargs)
#             else:
#                 return self.cell.mxm(
#                     self.utils.any_hyper_vector_to_hyper_row(other),
#                     *args,
#                     **kwargs
#                 )
#         else:
#             if self.utils.is_single_cell(other):
#                 return self._force_init_column().mxm(other, *args, **kwargs)
#             else:
#                 return self._force_init_row().mxm(
#                     self.utils.any_hyper_vector_to_hyper_matrix(other),
#                     *args,
#                     **kwargs
#                 )
#
#     def rmxm(self, other: Matrix, *args, **kwargs) -> Matrix:
#         if self.cell is not None:
#             if self.utils.is_single_cell(other):
#                 return self.cell.rmxm(other, *args, **kwargs)
#             else:
#                 return self.cell.rmxm(
#                     self.utils.any_hyper_vector_to_hyper_column(other),
#                     *args,
#                     **kwargs
#                 )
#         else:
#             if self.utils.is_single_cell(other):
#                 return self._force_init_row().rmxm(other, *args, **kwargs)
#             else:
#                 return self._force_init_column().rmxm(
#                     self.utils.any_hyper_vector_to_hyper_matrix(other),
#                     *args,
#                     **kwargs
#                 )
#
#     def r_complimentary_mask(self, other: Matrix) -> Matrix:
#         if self.cell is not None:
#             assert self.utils.is_single_cell(other)
#             return self.cell.r_complimentary_mask(other)
#         if self.utils.is_hyper_column(other):
#             if self.column is not None:
#                 return self.column.r_complimentary_mask(other)
#             return self.row.r_complimentary_mask(
#                 self.utils.hyper_column_to_hyper_row(other)
#             )
#         assert self.utils.is_hyper_row(other)
#         if self.row is not None:
#             return self.row.r_complimentary_mask(other)
#         return self.column.r_complimentary_mask(
#             self.utils.hyper_row_to_hyper_column(other)
#         )
#
#     def __iadd__(self, other: Matrix) -> "EnhancedMatrix":
#         if self.cell is not None:
#             assert self.utils.is_single_cell(other)
#             self.cell.__iadd__(other)
#         else:
#             if self.row is not None:
#                 self.row.__iadd__(self.utils.any_hyper_vector_to_hyper_row(other))
#             if self.column is not None:
#                 self.column.__iadd__(self.utils.any_hyper_vector_to_hyper_column(other))
#         return self
#
#     def with_format(self, format: MatrixFormat) -> "EnhancedMatrix":
#         return HyperMatrix(self.hyper_size,
#                            base_factory=lambda m: self.base.with_format(format) if m is None else self.base_factory(m))


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
