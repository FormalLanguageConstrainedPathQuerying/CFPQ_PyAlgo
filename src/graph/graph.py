from pathlib import Path
from tqdm import tqdm

from pygraphblas import Matrix, BOOL
from src.graph.index_graph import SAVEMIDDLETYPE
from src.graph.length_graph import SAVELENGTHTYPE

from src.utils.graph_size import get_graph_size


class Graph:
    def __init__(self):
        self.path = "path/to/graph"
        self.type = None
        self.matrices_size = 0
        self.matrices = dict()

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(self.type, self.matrices_size, self.matrices_size)
        return self.matrices[item]

    def __setitem__(self, key, value):
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()

    def get_number_of_vertices(self):
        return self.matrices_size

    def get_number_of_edges(self):
        return sum([self.matrices[label].nvals for label in self.matrices])

    @classmethod
    def from_txt(cls, path: Path):
        graph = Graph()
        graph.path = path
        return graph

    def load_bool_graph(self, verbose=False):
        self.type = BOOL
        self.matrices_size = get_graph_size(self.path)

        with open(self.path, "r") as f:
            for line in tqdm(f.readlines()) if verbose else f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)

                if label not in self.matrices:
                    self.matrices[label] = Matrix.sparse(self.type, self.matrices_size, self.matrices_size)

                self.matrices[label][v, to] = True

    def load_save_middle_graph(self, verbose=False):
        self.type = SAVEMIDDLETYPE
        self.matrices_size = get_graph_size(self.path)

        with open(self.path, "r") as f:
            for line in tqdm(f.readlines()) if verbose else f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)

                if label not in self.matrices:
                    self.matrices[label] = Matrix.sparse(self.type, self.matrices_size, self.matrices_size)

                self.matrices[label][v, to] = (v, to, v, 1, 1)

    def load_save_length_graph(self, verbose=False):
        self.type = SAVELENGTHTYPE
        self.matrices_size = get_graph_size(self.path)

        with open(self.path, "r") as f:
            for line in tqdm(f.readlines()) if verbose else f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)

                if label not in self.matrices:
                    self.matrices[label] = Matrix.sparse(self.type, self.matrices_size, self.matrices_size)

                self.matrices[label][v, to] = (v, to, v, 1)
