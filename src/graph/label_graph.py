import numpy as np
from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL

MAX_MATRIX_SIZE = 1000000


class LabelGraph:
    def __init__(self, matrices_size=MAX_MATRIX_SIZE):
        self.matrices = {}
        self.matrices_size = matrices_size

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(BOOL, self.matrices_size, self.matrices_size)
        return self.matrices[item]

    def __setitem__(self, key, value):
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()

    @classmethod
    def from_txt(cls, path):
        g = LabelGraph(get_graph_size(path))
        with open(path, 'r') as f:
            for line in f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)
                g[label][v, to] = True
        return g

    def chunkify(self, chunk_len):
        return list(map(list, np.array_split(np.arange(self.matrices_size), chunk_len)))


def get_graph_size(path):
    res = -1
    with open(path, 'r') as f:
        for line in f.readlines():
            v, label, to = line.split()
            v, to = int(v), int(to)
            res = max(res, v, to)
    return res + 1

