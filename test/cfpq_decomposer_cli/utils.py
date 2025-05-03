from dataclasses import dataclass
from typing import Tuple

from graphblas.core.matrix import Matrix

from cfpq_decomposer.high_performance_decomposer import HighPerformanceDecomposer
from cfpq_matrix.matrix_utils import stack


@dataclass
class DecomposerCliMetrics:
    s_edges: int
    compression_factor: float
    is_valid: bool

def parse_decomposer_cli_output(output: str) -> DecomposerCliMetrics:
    lines = output.strip().splitlines()
    sedges_line = next(l for l in lines if l.startswith('#SEdges'))
    s_edges = int(sedges_line.split()[1])
    cf_line = next(l for l in lines if l.startswith('Compression factor'))
    compression_factor = float(cf_line.split()[2])
    valid_line = next(l for l in lines if l.startswith('Is compression valid'))
    is_valid = valid_line.split()[3] == 'True'
    return DecomposerCliMetrics(
        s_edges=s_edges,
        compression_factor=compression_factor,
        is_valid=is_valid
    )

class CorruptDecomposer(HighPerformanceDecomposer):
    def decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        left, right = super().decompose(matrix)
        nrows, _ = left.shape
        _, ncols = right.shape

        rows = list(range(nrows))
        cols = [0] * nrows
        extra_col = Matrix.from_coo(rows, cols, True, nrows=nrows, ncols=1)

        rows2 = [0] * ncols
        cols2 = list(range(ncols))
        extra_row = Matrix.from_coo(rows2, cols2, True, nrows=1, ncols=ncols)

        return stack([[left, extra_col]]), stack([[right], [extra_row]])
