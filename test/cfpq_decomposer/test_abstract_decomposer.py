from abc import ABC, abstractmethod
from typing import Tuple

from graphblas.core.matrix import Matrix
from graphblas.core.dtypes import BOOL
import numpy as np
import graphblas

from cfpq_decomposer.decomposer import Decomposer

class TestAbstractDecomposer(ABC):
    @abstractmethod
    def create_decomposer(self) -> Decomposer:
        pass

    def decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        return self.create_decomposer().decompose(matrix)

    def test_decompose_similar_rows_matrix(self):
        nrows, ncols = 15, 15
        M = Matrix(BOOL, nrows=nrows, ncols=ncols)
        base_row_indices = [0, 1, 2, 3, 4, 5]
        for i in range(10):
            if i % 3 == 0:
                M[i, 3] = True
            for j in base_row_indices:
                M[i, j] = True
        for i in range(10, nrows):
            M[i, i % ncols] = True
        LEFT, RIGHT = self.decompose(M)
        LEFT_RIGHT: Matrix = LEFT.mxm(RIGHT, op=graphblas.semiring.any_pair).new(dtype=BOOL)

        assert LEFT_RIGHT.dup(mask=~M.S).nvals == 0
        assert LEFT_RIGHT.nvals >= 18

    def test_decompose_multiple_patterns(self):
        nrows, ncols = 300, 100
        M = Matrix(BOOL, nrows=nrows, ncols=ncols)

        pattern1_cols = set(range(20))
        for i in range(100):
            for j in pattern1_cols:
                M[i, j] = True
            if i % 10 == 0:
                M[i, 25] = True

        pattern2_cols = set(range(30, 50))
        for i in range(100, 200):
            for j in pattern2_cols:
                M[i, j] = True
            if i % 15 == 0:
                M[i, 55] = True

        pattern3_cols = set(range(60, 80))
        for i in range(200, 300):
            for j in pattern3_cols:
                M[i, j] = True
            if i % 20 == 0:
                M[i, 85] = True

        LEFT, RIGHT = self.decompose(M)
        LEFT_RIGHT = LEFT.mxm(RIGHT, op=graphblas.semiring.any_pair).new(dtype=BOOL)

        assert M.nvals == 6022
        assert LEFT_RIGHT.nvals >= 6000
        assert (LEFT_RIGHT | LEFT_RIGHT).new(mask=~M.S).nvals == 0

    def test_decompose_double_thresholding(self):
        nrows, ncols = 100, 50
        M = Matrix(BOOL, nrows=nrows, ncols=ncols)

        for i in range(nrows):
            for j in range(10):
                M[i, j] = True

        for i in range(75):
            for j in range(10, 20):
                M[i, j] = True

        for i in range(74):
            for j in range(20, 30):
                M[i, j] = True

        for i in range(76):
            for j in range(30, 40):
                M[i, j] = True

        for i in range(80):
            for j in range(40, 50):
                M[i, j] = True

        # Call the decompose function
        LEFT, RIGHT = self.decompose(M)
        LEFT_RIGHT = LEFT.mxm(RIGHT, op=graphblas.semiring.any_pair).new(dtype=BOOL)

        assert M.nvals == 4050
        assert LEFT_RIGHT.nvals >= 4000
        assert (LEFT_RIGHT | LEFT_RIGHT).new(mask=~M.S).nvals == 0

    def test_decompose_similar_columns_without_transpose(self):
        nrows, ncols = 100, 200
        M: Matrix = Matrix(BOOL, nrows=nrows, ncols=ncols)

        for j in range(50):
            for i in range(80):
                M[i, j] = True
            if j % 10 == 0:
                for i in range(80, 85):
                    M[i, j] = True

        for i in range(nrows):
            for _ in range(5):
                j = np.random.randint(50, ncols)
                M[i, j] = True

        LEFT, RIGHT = self.decompose(M)
        LEFT_RIGHT = LEFT.mxm(RIGHT, op=graphblas.semiring.any_pair).new(dtype=BOOL)

        assert M.nvals in range(4400, 4600)
        assert LEFT_RIGHT.nvals >= 3900
        assert (LEFT_RIGHT | LEFT_RIGHT).new(mask=~M.S).nvals == 0

    def test_decompose_random_matrix_with_patterns(self):
        nrows, ncols = 500, 500
        M = Matrix(BOOL, nrows=nrows, ncols=ncols)

        for group in range(5):
            row_start = group * 100
            row_end = row_start + 100
            cols = np.random.choice(ncols, size=50, replace=False)
            for i in range(row_start, row_end):
                for j in cols:
                    M[i, j] = True
                if i % 25 == 0:
                    extra_cols = np.random.choice(ncols, size=5, replace=False)
                    for j in extra_cols:
                        M[i, j] = True

        for group in range(5):
            col_start = group * 100
            col_end = col_start + 100
            rows = np.random.choice(nrows, size=50, replace=False)
            for j in range(col_start, col_end):
                for i in rows:
                    M[i, j] = True
                if j % 25 == 0:
                    extra_rows = np.random.choice(nrows, size=5, replace=False)
                    for i in extra_rows:
                        M[i, j] = True

        num_noise_entries = int(M.nvals * 0.05)
        for _ in range(num_noise_entries):
            i = np.random.randint(0, nrows)
            j = np.random.randint(0, ncols)
            M[i, j] = True

        LEFT, RIGHT = self.decompose(M)
        LEFT_RIGHT = LEFT.mxm(RIGHT, op=graphblas.semiring.any_pair).new(dtype=BOOL)

        assert M.nvals in range(48_000, 52_000)
        assert LEFT_RIGHT.nvals >= 33_000
        assert (LEFT_RIGHT | LEFT_RIGHT).new(mask=~M.S).nvals == 0
