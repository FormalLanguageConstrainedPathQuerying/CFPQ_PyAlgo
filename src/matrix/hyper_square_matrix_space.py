from typing import Tuple, List

import graphblas.ss
from graphblas.core.matrix import Matrix
import graphblas.monoid

from src.matrix.enhanced_matrix import EnhancedMatrix
from src.matrix.hyper_matrix import HyperMatrix, CellHyperMatrix, VectorHyperMatrix
from src.matrix.hyper_matrix_space import HyperMatrixSpace, HyperVectorOrientation


class HyperSquareMatrixSpace(HyperMatrixSpace):
    def __init__(self, n: int, hyper_size: int):
        assert n >= 0
        assert hyper_size >= 1
        self.n = n
        self.raw_hyper_size = hyper_size
        self.rounded_hyper_size = hyper_size

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
            input_orientation = self.get_hyper_orientation(hyper_vector_or_cell.shape)
            (rows, columns, values) = hyper_vector_or_cell.to_coo()
            if input_orientation == HyperVectorOrientation.VERTICAL:
                rows = rows % self.n
            elif input_orientation == HyperVectorOrientation.HORIZONTAL:
                columns = columns % self.n
            else:
                assert False
            return Matrix.from_coo(
                rows,
                columns,
                values,
                nrows=self.n,
                ncols=self.n,
                # FIXME bool specific code
                dup_op=graphblas.monoid.any
            )

    def hyper_rotate(self, hyper_vector: Matrix, orientation: HyperVectorOrientation) -> Matrix:
        input_orientation = self.get_hyper_orientation(hyper_vector.shape)
        if input_orientation == orientation:
            return hyper_vector
        (rows, columns, values) = hyper_vector.to_coo()
        if orientation == HyperVectorOrientation.VERTICAL:
            rows = rows + (columns // self.n * self.n)
            columns = columns % self.n
        elif orientation == HyperVectorOrientation.HORIZONTAL:
            columns = columns + (rows // self.n * self.n)
            rows = rows % self.n
        else:
            assert False

        return Matrix.from_coo(rows, columns, values, nrows=hyper_vector.ncols, ncols=hyper_vector.nrows)

    def to_block_diag_matrix(self, hyper_vector: Matrix) -> Matrix:
        input_orientation = self.get_hyper_orientation(hyper_vector.shape)
        (rows, columns, values) = hyper_vector.to_coo()
        if input_orientation == HyperVectorOrientation.VERTICAL:
            columns = columns + (rows // self.n * self.n)
        elif input_orientation == HyperVectorOrientation.HORIZONTAL:
            rows = rows + (columns // self.n * self.n)
        else:
            assert False

        return Matrix.from_coo(
            rows, columns, values,
            nrows=self.n * self.rounded_hyper_size,
            ncols=self.n * self.rounded_hyper_size
        )

    def create_hyper_vector(self, typ, orientation: HyperVectorOrientation) -> Matrix:
        shape = {
            HyperVectorOrientation.VERTICAL: (self.n * self.rounded_hyper_size, self.n),
            HyperVectorOrientation.HORIZONTAL: (self.n, self.n * self.rounded_hyper_size)
        }[orientation]
        return Matrix(dtype=typ, nrows=shape[0], ncols=shape[1])

    def create_hyper_cell(self, typ) -> Matrix:
        return Matrix(dtype=typ, nrows=self.n, ncols=self.n)

    def stack_into_hyper_column(self, matrices: List[Matrix]) -> Matrix:
        assert len(matrices) == self.raw_hyper_size
        tiles = [[m] for m in matrices]
        zero = Matrix(matrices[0].dtype, self.n, self.n)
        for i in range(self.raw_hyper_size, self.rounded_hyper_size):
            tiles.append([zero])
        return graphblas.ss.concat(tiles)

    def repeat_into_hyper_column(self, matrix: Matrix) -> Matrix:
        return self.stack_into_hyper_column([matrix] * self.raw_hyper_size)

    def wrap_enhanced_hyper_matrix(self, base: EnhancedMatrix) -> HyperMatrix:
        return CellHyperMatrix(base, self) if self.is_single_cell(base.shape) else VectorHyperMatrix(base, self)
