import random
from collections import defaultdict
from typing import Any, Tuple

import graphblas
import numpy as np
from graphblas.binary import plus
from graphblas.core.dtypes import DataType, BOOL, INT32
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

def row_based_decompose(M: Matrix):
    """
    Decomposes a sparse boolean matrix M into LEFT, RIGHT, and M' such that M = LEFT * RIGHT + M'.

    Parameters:
    M (gb.Matrix): Input sparse boolean matrix.

    Returns:
    LEFT (gb.Matrix): Left factor matrix.
    RIGHT (gb.Matrix): Right factor matrix.
    M_prime (gb.Matrix): Remainder matrix after decomposition.
    """
    n_rows, n_cols = M.shape

    I, J, V = M.to_coo()

    rows = defaultdict(set)
    for i, j in zip(I, J):
        rows[i].add(j)

    p = 2147483647
    num_hashes = 5  # TODO 2 or 3 is probably better for real world data
    hash_funcs = []
    for _ in range(num_hashes):
        a = random.randint(1, p - 1)
        b = random.randint(0, p - 1)
        hash_funcs.append((a, b))

    minhashes = dict()

    for i, S_i in rows.items():
        minhash_values = []
        if len(S_i) < 5:
            continue
        for a, b in hash_funcs:
            min_hash = min(((a * x + b) % p) for x in S_i)
            minhash_values.append(min_hash)
        minhashes[i] = tuple(minhash_values)

    master_hashes = dict()
    for i, minhash_values in minhashes.items():
        master_hash = hash(minhash_values)
        master_hashes[i] = master_hash

    buckets = defaultdict(list)
    for i, master_hash in master_hashes.items():
        buckets[master_hash].append(i)

    buckets = {h: idxs for h, idxs in buckets.items() if len(idxs) >= 5}

    LEFT_columns = []
    RIGHT_rows = []

    for h, B in buckets.items():
        N = len(B)
        M_B: Matrix = M[B, :].new()
        A1 = M_B.dup(dtype=INT32).reduce_columnwise(plus).new()

        threshold = int(0.95 * N)
        A2: Vector = A1.select('>=', threshold).new()

        if A2.nvals == 0:
            continue

        S_A2 = set(A2.to_coo()[0])

        B_prime = [i for i in B if S_A2 <= rows[i]]

        K = len(B_prime)
        if K == 0:
            continue

        M_B_prime = M[B_prime, :].new()
        A3 = M_B_prime.dup(dtype=INT32).reduce_columnwise(plus)

        threshold = int(0.95 * K)
        A4 = A3.select('>=', threshold).new()

        if A4.nvals == 0:
            continue

        S_A4 = set(A4.to_coo()[0])

        B_double_prime = [i for i in B_prime if S_A4 <= rows[i]]

        if len(B_double_prime) < 5:
            continue

        RIGHT_rows.append(A4)

        CORE = Vector(BOOL, size=n_rows)
        for i in B_double_prime:
            CORE[i] = True
        LEFT_columns.append(CORE)

    num_buckets_remaining = len(LEFT_columns)
    if num_buckets_remaining == 0:
        return Matrix(M.dtype, M.nrows, 0), Matrix(M.dtype, 0, M.ncols)

    LEFT = Matrix(bool, n_rows, num_buckets_remaining)
    for idx, CORE in enumerate(LEFT_columns):
        LEFT[:, idx] = CORE

    RIGHT = Matrix(bool, num_buckets_remaining, n_cols)
    for idx, A4 in enumerate(RIGHT_rows):
        RIGHT[idx, :] = A4

    return LEFT, RIGHT

def column_based_decompose(M: Matrix):
    LEFT_T, RIGHT_T = row_based_decompose(M.T.new())
    return RIGHT_T.T.new(), LEFT_T.T.new()

def decompose(M: Matrix):
    accumulated_LEFT = []
    accumulated_RIGHT = []
    iteration = 0

    init_nvals = M.nvals
    if init_nvals == 0:
        return Matrix(M.dtype, M.nrows, 0), Matrix(M.dtype, 0, M.ncols)

    while True:
        iteration += 1
        nvals_before = M.nvals

        LEFT1, RIGHT1 = row_based_decompose(M)

        if LEFT1.nvals != 0:
            M = M.dup(mask=~LEFT1.mxm(RIGHT1, op=graphblas.semiring.any_pair).new(dtype=BOOL).S)

        LEFT2, RIGHT2 = column_based_decompose(M)

        if LEFT2.nvals != 0:
            M = M.dup(mask=~LEFT2.mxm(RIGHT2, op=graphblas.semiring.any_pair).new(dtype=BOOL).S)

        nvals_LEFT_RIGHT = LEFT1.nvals + RIGHT1.nvals + LEFT2.nvals + RIGHT2.nvals

        nvals_after = M.nvals
        delta_M = nvals_before - nvals_after

        reduction_ratio = delta_M / nvals_before if nvals_before > 0 else 0
        size_ratio = nvals_LEFT_RIGHT / delta_M if delta_M > 0 else float('inf')

        accumulated_LEFT.extend([LEFT1, LEFT2])
        accumulated_RIGHT.extend([RIGHT1, RIGHT2])

        if reduction_ratio < 0.05 or size_ratio > 0.3:
            break

        if M.nvals == 0:
            break

    if not accumulated_LEFT or not accumulated_RIGHT:
        return Matrix(BOOL, nrows=M.nrows, ncols=0), Matrix(BOOL, nrows=0, ncols=M.ncols)

    LEFT = stack([accumulated_LEFT])
    RIGHT = stack([[RIGHT] for RIGHT in accumulated_RIGHT])

    return LEFT, RIGHT

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
