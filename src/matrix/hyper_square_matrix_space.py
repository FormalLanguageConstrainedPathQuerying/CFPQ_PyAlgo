from typing import Tuple, List

from pygraphblas import Matrix

from src.matrix.enhanced_matrix import EnhancedMatrix
from src.matrix.hyper_matrix import HyperMatrix, CellHyperMatrix, VectorHyperMatrix
from src.matrix.hyper_matrix_space import HyperMatrixSpace, HyperVectorOrientation
from src.matrix.hyper_matrix_utils import HyperMatrixUtils
from src.matrix.iadd_optimized_matrix import IAddOptimizedMatrix
from src.matrix.matrix_to_enhanced_adapter import MatrixToEnhancedAdapter


class HyperSquareMatrixSpace(HyperMatrixSpace):
    def __init__(self, n: int, hyper_size: int):
        assert n >= 0
        assert hyper_size >= 1
        self.n = n
        self.raw_hyper_size = hyper_size
        self.rounded_hyper_size = 2 ** (hyper_size - 1).bit_length()
        # TODO inline hyper_utils
        self.hyper_utils = HyperMatrixUtils(n, self.rounded_hyper_size)

    def is_single_cell(self, matrix_shape: Tuple[int, int]) -> bool:
        return matrix_shape == (self.n, self.n)

    def is_hyper_vector(self, matrix_shape: Tuple[int, int]) -> bool:
        return matrix_shape in [(self.n * self.rounded_hyper_size, self.n), (self.n, self.n * self.rounded_hyper_size)]

    def get_hyper_orientation(self, matrix_shape: Tuple[int, int]) -> HyperVectorOrientation:
        return {
            (self.n * self.rounded_hyper_size, self.n): HyperVectorOrientation.VERTICAL,
            (self.n, self.n * self.rounded_hyper_size): HyperVectorOrientation.HORIZONTAL
        }[matrix_shape]

    def reduce_hyper_vector_or_cell(self, hyper_vector_or_cell: Matrix) -> Matrix:
        if self.is_single_cell(hyper_vector_or_cell.shape):
            return hyper_vector_or_cell
        else:
            return {
                HyperVectorOrientation.VERTICAL: lambda: self.hyper_utils.reduce_hyper_column(hyper_vector_or_cell),
                HyperVectorOrientation.HORIZONTAL: lambda: self.hyper_utils.reduce_hyper_row(hyper_vector_or_cell)
            }[self.get_hyper_orientation(hyper_vector_or_cell.shape)]()

    def hyper_rotate(self, hyper_vector: Matrix, orientation: HyperVectorOrientation) -> Matrix:
        return {
            HyperVectorOrientation.VERTICAL: lambda: self.hyper_utils.any_hyper_vector_to_hyper_column(hyper_vector),
            HyperVectorOrientation.HORIZONTAL: lambda: self.hyper_utils.any_hyper_vector_to_hyper_row(hyper_vector)
        }[orientation]()

    def to_block_diag_matrix(self, hyper_vector: Matrix) -> Matrix:
        return self.hyper_utils.any_hyper_vector_to_hyper_matrix(hyper_vector)

    def create_hyper_vector(self, typ, orientation: HyperVectorOrientation) -> Matrix:
        shape = {
            HyperVectorOrientation.VERTICAL: (self.n * self.rounded_hyper_size, self.n),
            HyperVectorOrientation.HORIZONTAL: (self.n, self.n * self.rounded_hyper_size)
        }[orientation]
        return Matrix.sparse(typ=typ, nrows=shape[0], ncols=shape[1])

    def stack_into_hyper_column(self, matrices: List[Matrix]) -> Matrix:
        assert len(matrices) == self.raw_hyper_size

        def create_hyper_column() -> Matrix:
            return self.create_hyper_vector(matrices[0].type, HyperVectorOrientation.VERTICAL)

        hyper_column = IAddOptimizedMatrix(MatrixToEnhancedAdapter(create_hyper_column()))
        for i, m in enumerate(matrices):
            cur_cell = create_hyper_column()
            cur_cell[(i * self.n):((i + 1) * self.n - 1), :] = m
            hyper_column += cur_cell
        return hyper_column.to_matrix()

    def wrap_enhanced_hyper_matrix(self, base: EnhancedMatrix) -> HyperMatrix:
        return CellHyperMatrix(base, self) if self.is_single_cell(base.shape) else VectorHyperMatrix(base, self)
