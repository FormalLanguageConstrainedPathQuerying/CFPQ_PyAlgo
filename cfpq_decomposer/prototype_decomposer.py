import random
from collections import defaultdict

from graphblas.binary import plus
from graphblas.core.dtypes import BOOL, INT32
from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector

from cfpq_decomposer.abstract_decomposer import AbstractDecomposer


class PrototypeDecomposer(AbstractDecomposer):
    def row_based_decompose(self, M: Matrix):
        n_rows, n_cols = M.shape

        I, J, V = M.to_coo()

        rows = defaultdict(set)
        for i, j in zip(I, J):
            rows[i].add(j)

        p = 2147483647
        num_hashes = 3
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
