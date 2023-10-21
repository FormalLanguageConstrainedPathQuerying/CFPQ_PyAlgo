import graphblas
from graphblas.core.matrix import Matrix

from src.matrix.enhanced_matrix import OPTIMIZE_EMPTY
from src.utils.unique_ptr import unique_ptr


class HyperMatrixUtils:
    def __init__(self, regular_size: int, hyper_size: int):
        assert regular_size >= 0
        assert hyper_size >= 1
        assert (hyper_size & (hyper_size-1) == 0), (f"Only power of 2 hyper sizes are supported, "
                                                    f"{hyper_size} isn't a power of 2")
        self.n = regular_size
        self.hyper_size = hyper_size

    def _hyper_rectangle_to_hyper_column(self, hyper_rectangle: Matrix, hyper_width: int) -> Matrix:
        if hyper_width == 1:
            return hyper_rectangle
        new_hyper_width = hyper_width // 2
        new_rectangle = unique_ptr(Matrix(hyper_rectangle.dtype, nrows=self.n * self.hyper_size, ncols=self.n * new_hyper_width))
        new_rectangle[(self.n * new_hyper_width):, :] << (
            hyper_rectangle[:(self.n * self.hyper_size) - (self.n * new_hyper_width), self.n * new_hyper_width:]
        )
        new_rectangle << new_rectangle.ewise_add(
            hyper_rectangle[:, :self.n * new_hyper_width],
            # FIXME bool specific code
            op=graphblas.monoid.any
        )
        return self._hyper_rectangle_to_hyper_column(new_rectangle, new_hyper_width)

    def hyper_row_to_hyper_column(self, hyper_row: Matrix) -> Matrix:
        assert hyper_row.nrows == self.n
        assert hyper_row.ncols == self.n * self.hyper_size
        if OPTIMIZE_EMPTY and hyper_row.nvals == 0:
            return unique_ptr(Matrix(hyper_row.dtype, hyper_row.ncols, hyper_row.nrows))
        hyper_rectangle = unique_ptr(hyper_row.dup())
        hyper_rectangle.resize(nrows=self.n * self.hyper_size, ncols=self.n * self.hyper_size)
        column = self._hyper_rectangle_to_hyper_column(hyper_rectangle, hyper_width=self.hyper_size)
        return column

    def _hyper_rectangle_to_hyper_row(self, hyper_rectangle: Matrix, hyper_height: int) -> Matrix:
        if hyper_height == 1:
            return hyper_rectangle
        new_hyper_height = hyper_height // 2
        new_rectangle = unique_ptr(Matrix(hyper_rectangle.dtype, nrows=self.n * new_hyper_height, ncols=self.n * self.hyper_size))
        new_rectangle[:, (self.n * new_hyper_height):] << (
            hyper_rectangle[self.n * new_hyper_height:, :(self.n * self.hyper_size) - (self.n * new_hyper_height)]
        )
        new_rectangle += new_rectangle.ewise_add(
            hyper_rectangle[:self.n * new_hyper_height, :],
            # FIXME bool specific code
            op=graphblas.monoid.any
        )
        return self._hyper_rectangle_to_hyper_row(new_rectangle, new_hyper_height)

    def hyper_column_to_hyper_row(self, hyper_column: Matrix) -> Matrix:
        assert hyper_column.nrows == self.n * self.hyper_size
        assert hyper_column.ncols == self.n
        if OPTIMIZE_EMPTY and hyper_column.nvals == 0:
            return unique_ptr(Matrix(hyper_column.dtype, hyper_column.ncols, hyper_column.nrows))
        hyper_rectangle = unique_ptr(hyper_column.dup())
        hyper_rectangle.resize(nrows=self.n * self.hyper_size, ncols=self.n * self.hyper_size)
        row = self._hyper_rectangle_to_hyper_row(hyper_rectangle, hyper_height=self.hyper_size)
        return row

    def _hyper_rectangle_to_hyper_sausage(self, hyper_rectangle: Matrix, hyper_height: int, hyper_width: int) -> Matrix:
        if hyper_height == 1:
            return hyper_rectangle
        new_hyper_height = hyper_height // 2
        new_hyper_width = hyper_width * 2
        new_rectangle = unique_ptr(Matrix(hyper_rectangle.dtype, nrows=self.n * new_hyper_height, ncols=self.n * new_hyper_width))
        new_rectangle[:, (self.n * hyper_width):] << (
            hyper_rectangle[self.n * new_hyper_height:, :]
        )
        new_rectangle[:, :(self.n * hyper_width)] << new_rectangle[:, :(self.n * hyper_width)].ewise_add(
            hyper_rectangle[:self.n * new_hyper_height, :],
            # FIXME bool specific code
            op=graphblas.monoid.any
        )
        return self._hyper_rectangle_to_hyper_sausage(new_rectangle, new_hyper_height, new_hyper_width)

    def _hyper_sausage_to_hyper_matrix(
            self,
            hyper_sausage: Matrix,
            hyper_height: int,
            hyper_width: int,
            hyper_offset: int = 1,
            total_hyper_offset: int = 0
    ) -> Matrix:
        if hyper_height == self.hyper_size:
            return hyper_sausage
        new_hyper_height = hyper_height * 2
        new_hyper_width = hyper_width // 2
        new_sausage = unique_ptr(Matrix(hyper_sausage.dtype, nrows=self.n * new_hyper_height,
                                    ncols=self.n * (new_hyper_width + total_hyper_offset + hyper_offset)))
        tmp = hyper_sausage[:, (self.n * new_hyper_width):]
        new_sausage[(self.n * hyper_height):, (self.n * hyper_offset):(self.n * hyper_offset + tmp.ncols)] = tmp
        tmp = hyper_sausage[:, :(self.n * new_hyper_width)]
        new_sausage[:(self.n * hyper_height), :tmp.ncols] = tmp
        return self._hyper_sausage_to_hyper_matrix(new_sausage, new_hyper_height, new_hyper_width, hyper_offset * 2,
                                                   total_hyper_offset=total_hyper_offset + hyper_offset)

    def hyper_column_to_hyper_matrix(self, hyper_column: Matrix) -> Matrix:
        hyper_rectangle = unique_ptr(hyper_column.dup())
        hyper_rectangle.resize(nrows=self.n * self.hyper_size, ncols=self.n * self.hyper_size)
        sausage = self._hyper_rectangle_to_hyper_sausage(hyper_rectangle, hyper_width=self.hyper_size,
                                                         hyper_height=self.hyper_size)
        matrix = self._hyper_sausage_to_hyper_matrix(sausage, hyper_width=self.hyper_size * self.hyper_size, hyper_height=1)
        matrix.resize(nrows=self.n * self.hyper_size, ncols=self.n * self.hyper_size)
        return matrix

    def _reduce_hyper_row(self, hyper_row: Matrix, hyper_size: int) -> Matrix:
        if hyper_size == 1:
            return hyper_row
        return self._reduce_hyper_row(
            unique_ptr(hyper_row[:, :(hyper_row.ncols // 2)].ewise_add(
                hyper_row[:, hyper_row.ncols // 2:],
                # FIXME bool specific code
                op=graphblas.monoid.any
            ).new()),
            hyper_size=hyper_size // 2
        )

    def reduce_hyper_row(self, hyper_row: Matrix) -> Matrix:
        return self._reduce_hyper_row(hyper_row, self.hyper_size)

    def _reduce_hyper_column(self, hyper_column: Matrix, hyper_size: int) -> Matrix:
        if hyper_size == 1:
            return hyper_column
        return self._reduce_hyper_column(
            unique_ptr((hyper_column[:(hyper_column.nrows // 2), :].ewise_add(
                hyper_column[hyper_column.nrows // 2:, :],
                # FIXME bool specific code
                op=graphblas.monoid.any
            )).new()),
            hyper_size=hyper_size // 2
        )

    def reduce_hyper_column(self, hyper_column: Matrix) -> Matrix:
        return self._reduce_hyper_column(hyper_column, self.hyper_size)

    def reduce_any(self, hyper_vector_or_cell: Matrix) -> Matrix:
        if self.is_single_cell(hyper_vector_or_cell):
            return hyper_vector_or_cell
        if self.is_hyper_row(hyper_vector_or_cell):
            return self.reduce_hyper_row(hyper_vector_or_cell)
        assert self.is_hyper_column(hyper_vector_or_cell)
        return self.reduce_hyper_column(hyper_vector_or_cell)

    def any_hyper_vector_to_hyper_row(self, hyper_vector: Matrix):
        if self.is_hyper_row(hyper_vector):
            return hyper_vector
        return self.hyper_column_to_hyper_row(hyper_vector)

    def is_hyper_row(self, hyper_vector):
        return hyper_vector.nrows == self.n and hyper_vector.ncols == self.n * self.hyper_size

    def any_hyper_vector_to_hyper_column(self, hyper_vector: Matrix):
        if self.is_hyper_column(hyper_vector):
            return hyper_vector
        return self.hyper_row_to_hyper_column(hyper_vector)

    def is_hyper_column(self, hyper_vector):
        return hyper_vector.nrows == self.n * self.hyper_size and hyper_vector.ncols == self.n

    def any_hyper_vector_to_hyper_matrix(self, hyper_vector: Matrix):
        # TODO direct conversion of hyper_row to hyper matrix
        return self.hyper_column_to_hyper_matrix(
            self.any_hyper_vector_to_hyper_column(hyper_vector)
        )

    def is_single_cell(self, matrix: Matrix):
        return matrix.nrows == self.n and matrix.ncols == self.n