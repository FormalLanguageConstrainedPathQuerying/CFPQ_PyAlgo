import graphblas
from graphblas.core.matrix import Matrix


def complimentary_mask(matrix: Matrix, mask: Matrix) -> Matrix:
    zero = Matrix(matrix.dtype, nrows=matrix.nrows, ncols=matrix.ncols)
    zero.ss.config["format"] = matrix.ss.config["format"]
    res = Matrix(matrix.dtype, nrows=matrix.nrows, ncols=matrix.ncols)
    res.ss.config["format"] = matrix.ss.config["format"]
    res(~mask.S) << zero.ewise_add(matrix, op=graphblas.monoid.any)
    return res
