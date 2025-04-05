import numpy as np
from graphblas import semiring
from graphblas.core.dtypes import INT64, BOOL, INT32
from graphblas.core.matrix import Matrix

from cfpq_decomposer.abstract_decomposer import AbstractDecomposer
from cfpq_decomposer.constants import HASH_PRIME_MODULUS, HASH_COUNT, MIN_LSH_BUCKET_SIZE


class HighPerformanceDecomposer(AbstractDecomposer):
    def row_based_decompose(self, matrix: Matrix) -> tuple[Matrix, Matrix]:
        n_rows, n_cols = matrix.shape

        a = np.random.randint(1, HASH_PRIME_MODULUS, size=HASH_COUNT, dtype=np.int64)
        b = np.random.randint(0, HASH_PRIME_MODULUS, size=HASH_COUNT, dtype=np.int64)

        cols = np.arange(n_cols, dtype=np.int64)
        H_vals = ((cols[:, None] * a[None, :]) + b[None, :]) % HASH_PRIME_MODULUS

        H_gb = Matrix.from_dense(H_vals)

        S = Matrix(INT64, n_rows, HASH_COUNT)
        S << semiring.min_second(matrix @ H_gb)

        r, c, v = S.to_coo()
        signature = np.zeros((n_rows, HASH_COUNT), dtype=np.int64)
        signature[r, c] = v

        weights = np.random.default_rng().integers(
            low=1, high=np.iinfo(np.uint64).max,
            size=signature.shape[1], dtype=np.uint64
        )

        row_hashes = (signature.astype(np.uint64) @ weights)  # shape (n_rows,)

        _, inv, counts = np.unique(
            row_hashes, return_inverse=True, return_counts=True
        )

        valid = counts >= MIN_LSH_BUCKET_SIZE
        row_bucket = np.where(valid[inv], inv, -1)

        valid_ids = np.nonzero(valid)[0]
        b = len(valid_ids)
        lut = np.full_like(counts, -1, dtype=np.int64)
        lut[valid_ids] = np.arange(b, dtype=np.int64)
        new_bucket = np.where(row_bucket >= 0, lut[row_bucket], -1)

        keep = new_bucket >= 0
        LEFT = Matrix.from_coo(
            rows=np.nonzero(keep)[0].astype(np.uint64),
            columns=new_bucket[keep].astype(np.uint64),
            values=np.ones(int(keep.sum()), dtype=bool),
            dtype=BOOL,
            nrows=n_rows,
            ncols=b
        )

        LEFT_int = LEFT.dup(dtype=INT32)
        M_int = matrix.dup(dtype=INT32)

        O = Matrix(INT32, b, n_cols)
        O << semiring.plus_times(LEFT_int.T @ M_int)

        bucket_sizes = counts[valid_ids].astype(np.int32)

        orow, ocol, oval = O.to_coo()
        keep_core = oval >= bucket_sizes[orow]

        RIGHT = Matrix.from_coo(
            rows=orow[keep_core].astype(np.uint64),
            columns=ocol[keep_core].astype(np.uint64),
            values=np.ones(int(keep_core.sum()), dtype=bool),
            dtype=BOOL,
            nrows=b,
            ncols=n_cols
        )

        return LEFT, RIGHT
