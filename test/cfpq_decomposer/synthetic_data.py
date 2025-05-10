import numpy as np
from graphblas.core.dtypes import BOOL
from graphblas.core.matrix import Matrix

# extremely conservative lower bounds are used to avoid flaky tests
MIN_COMPRESSION_FACTORS = {
    "similar_rows": 1.5,
    "multiple_patterns": 6,
    "double_threshold": 8,
    "similar_columns": 3.0,
    "random_patterns": 2.5,
}

def similar_rows_matrix():
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
    return M

def multiple_patterns_matrix():
    nrows, ncols = 300, 100
    M = Matrix(BOOL, nrows=nrows, ncols=ncols)
    for i in range(100):
        for j in range(20):
            M[i, j] = True
        if i % 10 == 0:
            M[i, 25] = True
    for i in range(100, 200):
        for j in range(30, 50):
            M[i, j] = True
        if i % 15 == 0:
            M[i, 55] = True
    for i in range(200, 300):
        for j in range(60, 80):
            M[i, j] = True
        if i % 20 == 0:
            M[i, 85] = True
    return M

def double_threshold_matrix():
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
    return M

def similar_columns_matrix():
    nrows, ncols = 100, 200
    M = Matrix(BOOL, nrows=nrows, ncols=ncols)
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
    return M

def random_matrix_with_patterns():
    nrows, ncols = 500, 500
    M = Matrix(BOOL, nrows=nrows, ncols=ncols)
    for group in range(5):
        rows = range(group * 100, group * 100 + 100)
        cols = np.random.choice(ncols, size=50, replace=False)
        for i in rows:
            for j in cols:
                M[i, j] = True
            if i % 25 == 0:
                extra = np.random.choice(ncols, size=5, replace=False)
                for j in extra:
                    M[i, j] = True
    for group in range(5):
        cols = range(group * 100, group * 100 + 100)
        rows = np.random.choice(nrows, size=50, replace=False)
        for j in cols:
            for i in rows:
                M[i, j] = True
            if j % 25 == 0:
                extra = np.random.choice(nrows, size=5, replace=False)
                for i in extra:
                    M[i, j] = True
    noise = int(M.nvals * 0.05)
    for _ in range(noise):
        i = np.random.randint(0, nrows)
        j = np.random.randint(0, ncols)
        M[i, j] = True
    return M
