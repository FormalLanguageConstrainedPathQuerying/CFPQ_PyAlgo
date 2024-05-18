from typing import Tuple, List

from pygraphblas import Matrix
from pygraphblas.binaryop import BinaryOp

from cfpq_matrix.optimized_matrix import OptimizedMatrix
from cfpq_matrix.block.block_matrix import BlockMatrix, CellBlockMatrix, VectorBlockMatrix
from cfpq_matrix.block.block_matrix_space import BlockMatrixSpace, BlockMatrixOrientation


class BlockMatrixSpaceImpl(BlockMatrixSpace):
    def __init__(self, n: int, block_count: int):
        assert n >= 0
        assert block_count >= 1
        self.n = n
        self._block_count = block_count

    @property
    def block_count(self) -> int:
        return self._block_count

    def is_single_cell(self, matrix_shape: Tuple[int, int]) -> bool:
        return matrix_shape == (self.n, self.n)

    def is_hyper_vector(self, matrix_shape: Tuple[int, int]) -> bool:
        return matrix_shape in [
            (self.n * self.block_count, self.n),
            (self.n, self.n * self.block_count)
        ]

    def get_block_matrix_orientation(self, matrix_shape: Tuple[int, int]) -> BlockMatrixOrientation:
        return {
            (self.n * self.block_count, self.n): BlockMatrixOrientation.VERTICAL,
            (self.n, self.n * self.block_count): BlockMatrixOrientation.HORIZONTAL
        }[matrix_shape]

    def reduce_hyper_vector_or_cell(self, hyper_vector_or_cell: Matrix, op: BinaryOp) -> Matrix:
        if self.is_single_cell(hyper_vector_or_cell.shape):
            return hyper_vector_or_cell
        if hyper_vector_or_cell.nvals == 0:
            return self.create_cell(hyper_vector_or_cell.type)
        input_orientation = self.get_block_matrix_orientation(hyper_vector_or_cell.shape)
        rows = hyper_vector_or_cell.npI
        columns = hyper_vector_or_cell.npJ
        values = hyper_vector_or_cell.npV
        if input_orientation == BlockMatrixOrientation.VERTICAL:
            rows = rows % self.n
        elif input_orientation == BlockMatrixOrientation.HORIZONTAL:
            columns = columns % self.n
        else:
            assert False
        return Matrix.from_lists(
            rows.tolist(),
            columns.tolist(),
            values.tolist(),
            nrows=self.n,
            ncols=self.n,
            typ=hyper_vector_or_cell.type,
        )

    def hyper_rotate(self, hyper_vector: Matrix, orientation: BlockMatrixOrientation) -> Matrix:
        input_orientation = self.get_block_matrix_orientation(hyper_vector.shape)
        if input_orientation == orientation:
            return hyper_vector
        if hyper_vector.nvals == 0:
            return self.create_hyper_vector(hyper_vector.type, orientation)
        rows = hyper_vector.npI
        columns = hyper_vector.npJ
        values = hyper_vector.npV
        if orientation == BlockMatrixOrientation.VERTICAL:
            rows = rows + (columns // self.n * self.n)
            columns = columns % self.n
        elif orientation == BlockMatrixOrientation.HORIZONTAL:
            columns = columns + (rows // self.n * self.n)
            rows = rows % self.n
        else:
            assert False
        return Matrix.from_lists(
            rows.tolist(),
            columns.tolist(),
            values.tolist(),
            nrows=hyper_vector.ncols,
            ncols=hyper_vector.nrows,
            typ=hyper_vector.type,
        )

    def to_block_diag_matrix(self, hyper_vector: Matrix) -> Matrix:
        if hyper_vector.nvals == 0:
            return Matrix.sparse(hyper_vector.type, self.n * self.block_count, self.n * self.block_count)
        input_orientation = self.get_block_matrix_orientation(hyper_vector.shape)
        rows = hyper_vector.npI
        columns = hyper_vector.npJ
        values = hyper_vector.npV
        if input_orientation == BlockMatrixOrientation.VERTICAL:
            columns = columns + (rows // self.n * self.n)
        elif input_orientation == BlockMatrixOrientation.HORIZONTAL:
            rows = rows + (columns // self.n * self.n)
        else:
            assert False

        return Matrix.from_lists(
            rows.tolist(),
            columns.tolist(),
            values.tolist(),
            nrows=self.n * self.block_count,
            ncols=self.n * self.block_count,
            typ=hyper_vector.type,
        )

    def create_hyper_vector(self, typ, orientation: BlockMatrixOrientation) -> Matrix:
        shape = {
            BlockMatrixOrientation.VERTICAL: (self.n * self.block_count, self.n),
            BlockMatrixOrientation.HORIZONTAL: (self.n, self.n * self.block_count)
        }[orientation]
        return Matrix.sparse(typ=typ, nrows=shape[0], ncols=shape[1])

    def create_cell(self, typ) -> Matrix:
        return Matrix.sparse(typ=typ, nrows=self.n, ncols=self.n)

    def stack_into_hyper_column(self, matrices: List[Matrix]) -> Matrix:
        res = self.create_hyper_vector(matrices[0].type, BlockMatrixOrientation.VERTICAL)
        for i, matrix in enumerate(matrices):
            for (row, col, value) in matrix:
                res[i * self.n + row, col] = value
        return res

    def repeat_into_hyper_column(self, matrix: Matrix) -> Matrix:
        return self.stack_into_hyper_column([matrix] * self.block_count)

    def automize_block_operations(self, base: OptimizedMatrix) -> BlockMatrix:
        return (
            CellBlockMatrix(base, self)
            if self.is_single_cell(base.shape)
            else VectorBlockMatrix(base, self)
        )

    def get_hyper_vector_blocks(self, hyper_vector: Matrix) -> List[Matrix]:
        res = [Matrix.sparse(hyper_vector.type, self.n, self.n) for _ in range(self.block_count)]
        orientation = self.get_block_matrix_orientation(hyper_vector.shape)
        if orientation == BlockMatrixOrientation.HORIZONTAL:
            for (row, col, value) in hyper_vector:
                res[col // self.n][row, col % self.n] = value
        elif orientation == BlockMatrixOrientation.VERTICAL:
            for (row, col, value) in hyper_vector:
                res[row // self.n][row % self.n, col] = value
        else:
            assert False
        return res
