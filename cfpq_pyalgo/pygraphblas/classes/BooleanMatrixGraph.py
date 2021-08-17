from networkx import MultiDiGraph
from pyformlang.cfg import Terminal
from pygraphblas import Matrix, BOOL

__all__ = [
    "BooleanMatrixGraph",
]


class BooleanMatrixGraph:
    def __init__(self, matrices_size: int):
        self.matrices_size = matrices_size
        self.matrices = dict()

    def __getitem__(self, item) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(
                BOOL, self.matrices_size, self.matrices_size
            )
        return self.matrices[item]

    def __setitem__(self, key, value: Matrix):
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()

    @property
    def labels(self):
        return list(self.matrices.keys())

    @classmethod
    def from_multidigraph(cls, g: MultiDiGraph):
        bmg = BooleanMatrixGraph(g.number_of_nodes())

        for u, v, edge_labels in g.edges(data=True):
            for label in edge_labels.values():
                bmg[Terminal(label)][u, v] = 1

        return bmg
