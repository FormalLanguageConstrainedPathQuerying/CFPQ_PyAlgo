from typing import Any

from pygraphblas import Matrix, Vector, descriptor
from pygraphblas.types import Type


def complimentary_mask(matrix: Matrix, mask: Matrix) -> Matrix:
    larger_matrix = matrix if matrix.nvals > mask.nvals else mask
    zero = Matrix.sparse(matrix.type, nrows=matrix.nrows, ncols=matrix.ncols)
    zero.format = larger_matrix.format
    res = Matrix.sparse(matrix.type, nrows=matrix.nrows, ncols=matrix.ncols)
    res.format = larger_matrix.format
    zero.eadd(matrix, add_op=matrix.type.ANY, mask=mask, desc=descriptor.C & descriptor.S, out=res)
    return res


def identity_matrix(one: Any, dtype: Type, size: int) -> Matrix:
    return Matrix.from_diag(Vector.dense(
        typ=dtype,
        size=size,
        fill=one
    ))
