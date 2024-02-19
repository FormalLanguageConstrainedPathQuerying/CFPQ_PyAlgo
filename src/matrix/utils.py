from graphblas.core.matrix import Matrix
from graphblas.core.operator import Monoid


def complimentary_mask(matrix: Matrix, mask: Matrix, helper_monoid: Monoid) -> Matrix:
    zero = Matrix(matrix.dtype, nrows=matrix.nrows, ncols=matrix.ncols)
    zero.ss.config["format"] = matrix.ss.config["format"]
    res = Matrix(matrix.dtype, nrows=matrix.nrows, ncols=matrix.ncols)
    res.ss.config["format"] = matrix.ss.config["format"]
    res(~matrix.S) << matrix.ewise_add(mask, op=helper_monoid)
    return res
