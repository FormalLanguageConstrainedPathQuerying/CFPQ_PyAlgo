from typing import Any, Tuple

import graphblas
import numpy as np
from graphblas.binary import plus
from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector


def complimentary_mask(matrix: Matrix, mask: Matrix) -> Matrix:
    larger_matrix = matrix if matrix.nvals > mask.nvals else mask
    zero = Matrix(matrix.dtype, nrows=matrix.nrows, ncols=matrix.ncols)
    zero.ss.config["format"] = larger_matrix.ss.config["format"]
    res = Matrix(matrix.dtype, nrows=matrix.nrows, ncols=matrix.ncols)
    res.ss.config["format"] = larger_matrix.ss.config["format"]
    res(~mask.S) << zero.ewise_add(matrix, op=graphblas.monoid.any)
    return res


def identity_matrix(one: Any, dtype: DataType, size: int) -> Matrix:
    return Vector.from_scalar(
        value=one,
        size=size,
        dtype=dtype
    ).diag()

def expand_matrix(matrix: Matrix, new_shape: Tuple[int, int]) -> Matrix:
    (rows, columns, values) = matrix.to_coo()
    return Matrix.from_coo(rows, columns, values, dtype=matrix.dtype, nrows=new_shape[0], ncols=new_shape[1])

def stack(matrix_grid: list[list[Matrix]]) -> Matrix:
    """
    Stack a 2D list of matrices into a single larger matrix.
    Vertically stacks matrices within each row of the list, and then horizontally stacks the results.

    Parameters:
    matrix_grid (list[list[Matrix]]): A 2D list of matrices to stack.

    Returns:
    Matrix: The stacked matrix.
    """
    if not matrix_grid or not matrix_grid[0]:
        raise ValueError("The matrix grid cannot be empty.")

    num_cols = len(matrix_grid[0])
    for row in matrix_grid:
        if len(row) != num_cols:
            raise ValueError("All rows in the matrix grid must have the same number of matrices.")

    for row in matrix_grid:
        row_height = row[0].nrows
        for matrix in row:
            if matrix.nrows != row_height:
                raise ValueError("All matrices in the same row must have the same number of rows.")

    for col in range(num_cols):
        col_width = matrix_grid[0][col].ncols
        for row in matrix_grid:
            if row[col].ncols != col_width:
                raise ValueError("All matrices in the same column must have the same number of columns.")

    combined_rows = []
    combined_columns = []
    combined_values = []

    current_row_offset = 0

    for row in matrix_grid:
        current_col_offset = 0

        for matrix in row:
            M_I, M_J, M_V = matrix.to_coo()

            adjusted_rows = M_I + current_row_offset
            adjusted_columns = M_J + current_col_offset

            combined_rows.append(adjusted_rows)
            combined_columns.append(adjusted_columns)
            combined_values.append(M_V)

            current_col_offset += matrix.ncols

        current_row_offset += row[0].nrows

    final_rows = np.concatenate(combined_rows)
    final_columns = np.concatenate(combined_columns)
    final_values = np.concatenate(combined_values)

    total_rows = current_row_offset
    total_columns = sum(matrix.ncols for matrix in matrix_grid[0])

    return Matrix.from_coo(
        rows=final_rows,
        columns=final_columns,
        values=final_values,
        dtype=matrix_grid[0][0].dtype,
        nrows=total_rows,
        ncols=total_columns,
    )

def drop_zeros_inplace(matrix: Matrix) -> Matrix:
    matrix(matrix.V, replace=True) << matrix
    return matrix
