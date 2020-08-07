from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL


class LabelGraph:
    def __init__(self, matrices_size: int):
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
        triplets = list()
        size_matrices = 0
        with open(path, 'r') as f:
            for line in f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)

                if v > size_matrices:
                    size_matrices = v

                if to > size_matrices:
                    size_matrices = to

                triplets.append((v, label, to))

        g = LabelGraph(size_matrices + 1)

        for triplet in triplets:
            g[triplet[1]][triplet[0], triplet[2]] = True

        return g
