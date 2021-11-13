"""Base class for a Labeled Graph decomposed into Boolean Matrices"""
from typing import Dict

import networkx as nx
from pygraphblas import Matrix, BOOL

__all__ = [
    "BooleanMatrixGraph",
]


class BooleanMatrixGraph:
    """A Labeled Graph decomposed into Boolean Matrices class

    Parameters
    ----------
    vertices_count: `int`
        The number of vertices in the graph, specifies the size of the adjacency matrices
    """

    def __init__(self, vertices_count: int = 0):
        self._matrices: Dict[str, Matrix] = dict()
        self._matrices_size: int = vertices_count

    def __getitem__(self, label: str) -> Matrix:
        if label not in self._matrices:
            raise KeyError(f"{label}")
        return self._matrices[label]

    def __setitem__(self, label: str, matrix: Matrix) -> None:
        self._matrices[label] = matrix

    def __contains__(self, label: str) -> bool:
        return label in self._matrices

    @property
    def matrices_size(self):
        return self._matrices_size

    @classmethod
    def from_nx_graph(cls, graph: nx.MultiDiGraph):
        """Create a BooleanMatrixGraph from NetworkX MultiDiGraph

        Each edge is expected to have a "label" attribute

        Parameters
        ----------
        graph: nx.MultiDiGraph
            NetworkX MultiDiGraph

        Returns
        -------
        g: BooleanMatrixGraph
            BooleanMatrixGraph
        """
        g = cls(graph.number_of_nodes())

        for u, v, edge in graph.edges(data=True):
            if edge["label"] not in g._matrices:
                g._matrices[edge["label"]] = Matrix.sparse(
                    typ=BOOL, nrows=g._matrices_size, ncols=g._matrices_size
                )
            g[edge["label"]][u, v] = True

        return g
