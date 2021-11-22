"""Base class for a Labeled Graph decomposed into Boolean Matrices"""
from typing import Dict, List

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
        self._graph_vertices: List[int] = []

    def __getitem__(self, label: str) -> Matrix:
        if label not in self._matrices:
            raise KeyError(f"{label}")
        return self._matrices[label]

    def __setitem__(self, label: str, matrix: Matrix) -> None:
        self._matrices[label] = matrix

    def __contains__(self, label: str) -> bool:
        return label in self._matrices

    @property
    def matrices_size(self) -> int:
        """The number of rows and columns in the matrix (also the number of vertices in the graph)"""
        return self._matrices_size

    def get_graph_vertex(self, matrix_v: int) -> int:
        """Convert BooleanMatrixGraph vertex number to original NetworkX MultiDiGraph vertex number"""
        return self._graph_vertices[matrix_v]

    @classmethod
    def from_nx_graph(cls, graph: nx.MultiDiGraph):
        """Create a BooleanMatrixGraph from NetworkX MultiDiGraph

        Its Nodes are expected to be `int`. Each edge is expected to have a "label" attribute.

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
        vertices: Dict[int, int] = dict()
        vertex_num: int = 0
        for u, v, edge in graph.edges(data=True):
            if u not in vertices:
                vertices[u] = vertex_num
                u = vertex_num
                vertex_num += 1
            else:
                u = vertices[u]
            if v not in vertices:
                vertices[v] = vertex_num
                v = vertex_num
                vertex_num += 1
            else:
                v = vertices[v]

            label = edge["label"]
            if label not in g._matrices:
                g._matrices[label] = Matrix.sparse(
                    typ=BOOL, nrows=g._matrices_size, ncols=g._matrices_size
                )
            g[label][u, v] = True
        g._graph_vertices = list(
            map(lambda x: x[0], sorted(vertices.items(), key=lambda x: x[1]))
        )
        return g
