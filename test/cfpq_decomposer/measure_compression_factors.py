# helper script needed to calculate safe values for
# compression factor test asserts

import numpy as np
import graphblas
from tqdm import tqdm
import graphblas as gb
from graphblas.core.matrix import Matrix
from graphblas.core.dtypes import BOOL

from cfpq_decomposer.high_performance_decomposer import HighPerformanceDecomposer
from cfpq_decomposer.prototype_decomposer import PrototypeDecomposer
from test.cfpq_decomposer.synthetic_data import similar_rows_matrix, multiple_patterns_matrix, double_threshold_matrix, \
    similar_columns_matrix, random_matrix_with_patterns

MATRIX_FNS = {
    "similar_rows": similar_rows_matrix,
    "multiple_patterns": multiple_patterns_matrix,
    "double_threshold": double_threshold_matrix,
    "similar_columns": similar_columns_matrix,
    "random_patterns": random_matrix_with_patterns,
}

def compute_case_quantile(gen_fn, runs=2500):
    values = []
    for cls in (HighPerformanceDecomposer, PrototypeDecomposer):
        desc = f"{gen_fn.__name__}::{cls.__name__}"
        for _ in tqdm(range(runs), desc=desc, leave=False):
            M = gen_fn()
            left, right = cls().decompose(M)
            left_right = left.mxm(right, op=graphblas.semiring.any_pair).new(dtype=BOOL)
            rem = M.dup(mask=~left_right.S).nvals
            values.append(M.nvals / (left.nvals + right.nvals + rem))
    return np.percentile(values, 0.1)

if __name__ == "__main__":
    quantiles = {}
    for key, fn in tqdm(MATRIX_FNS.items(), desc="Cases"):
        quantiles[key] = compute_case_quantile(fn)
    print("MIN_COMPRESSION_FACTORS = {")
    for key, val in quantiles.items():
        print(f'    "{key}": {val:.3f},')
    print("}")
