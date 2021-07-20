from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL
from tqdm import tqdm

from src.utils.common import chunkify
from src.utils.graph_size import get_graph_size

MAX_MATRIX_SIZE = 1000000


class LabelGraph:
    """
    This class representing label directed graph. supports only the functions necessary for the algorithms to work
    """
    def __init__(self, matrices_size=MAX_MATRIX_SIZE):
        self.matrices = {}
        self.matrices_size = matrices_size
        self.is_empty = True

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(BOOL, self.matrices_size, self.matrices_size)
        return self.matrices[item]

    def __setitem__(self, key, value):
        self.is_empty = False
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()

    def get_number_of_vertices(self):
        return self.matrices_size

    def get_number_of_edges(self):
        return sum([self.matrices[label].nvals for label in self.matrices])

    def clone(self):
        obj_copy = LabelGraph(self.matrices_size)
        for nonterm, matr in self.matrices.items():
            obj_copy[nonterm] = matr.dup()
        return obj_copy

    @classmethod
    def from_txt(cls, path, verbose=False):
        """
        Load graph from file in format triplets
        @param path: path to file
        @param verbose: flag to set the output of information on download
        @return: initialized class
        """
        g = LabelGraph(get_graph_size(path))
        with open(path, 'r') as f:
            for line in tqdm(f.readlines()) if verbose else f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)
                g[label][v, to] = True
        return g

    def chunkify(self, chunk_len) -> list:
        return list(chunkify(list(range(self.matrices_size)), chunk_len))

    def __add__(self, other):
        result = LabelGraph(self.matrices_size)

        if not self.is_empty and not other.is_empty:
            result.is_empty = False
        else:
            return result

        labels_only_in_self = set(self.matrices.keys()) - set(other.matrices.keys())
        labels_only_in_other = set(other.matrices.keys()) - set(self.matrices.keys())
        labels_in_both = set(self.matrices.keys()) & set(other.matrices.keys())
        for label in labels_in_both:
            result.matrices[label] = self.matrices[label] + other.matrices[label]

        for label in labels_only_in_other:
            result.matrices[label] = other.matrices[label]

        for label in labels_only_in_self:
            result.matrices[label] = self.matrices[label]

        return result

    def __iadd__(self, other):
        if not other.is_empty:
            self.is_empty = False

        for label in other.matrices:
            if label in self.matrices:
                self.matrices[label] = self.matrices[label] + other.matrices[label]
            else:
                self.matrices[label] = other.matrices[label]

        return self
