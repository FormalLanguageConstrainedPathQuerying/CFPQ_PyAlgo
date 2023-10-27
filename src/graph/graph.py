from collections import defaultdict
from pathlib import Path
from tqdm import tqdm

from pygraphblas import Matrix, BOOL

from graphblas.core.matrix import Matrix as GbMatrix
import graphblas.dtypes as gb_types

from src.graph.index_graph import SAVEMIDDLETYPE
from src.graph.length_graph import SAVELENGTHTYPE

from src.utils.graph_size import get_graph_size

import numpy as np


class Graph:
    def __init__(self):
        self.path = "path/to/graph"
        self.type = None
        self.matrices_size = 0
        self.matrices = dict()
        self.empty_matrix_factory = lambda: Matrix.sparse(self.type, self.matrices_size, self.matrices_size)

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = self.empty_matrix_factory()
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

    def load_python_graphblas_bool_graph(self, verbose=False):
        self.type = gb_types.BOOL
        self.matrices_size = 1

        coo_matrices = defaultdict(lambda: ([], []))

        import pandas as pd

        dfs = pd.read_csv(self.path, sep=' ', names=['start_vertex', 'label', 'end_vertex'],
                          dtype={'start_vertex': int, 'end_vertex': int}, chunksize=1_000_000)
        for df in tqdm(dfs) if verbose else dfs:
            groupby = df.groupby('label')

            for label, group in groupby:
                start_vertices = group['start_vertex']
                end_vertices = group['end_vertex']
                coo_matrices[label][0].append(np.array(start_vertices))
                coo_matrices[label][1].append(np.array(end_vertices))

        for label, (rows, cols) in coo_matrices.items():
            rows = np.concatenate(rows)
            cols = np.concatenate(cols)
            coo_matrices[label] = (rows, cols)
            self.matrices_size = max(self.matrices_size, rows.max() + 1, cols.max() + 1)

        self.empty_matrix_factory = lambda: GbMatrix(self.type, self.matrices_size, self.matrices_size)

        for k, v in coo_matrices.items():
            self.matrices[k] = GbMatrix.from_coo(
                rows=v[0],
                columns=v[1],
                values=True,
                nrows=self.matrices_size,
                ncols=self.matrices_size,
            )
