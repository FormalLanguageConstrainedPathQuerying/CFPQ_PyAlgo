from typing import Any

import graphblas
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
