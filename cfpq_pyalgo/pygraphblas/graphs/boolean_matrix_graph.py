"""Base class for a Labeled Graph decomposed into Boolean Matrices"""
from typing import Dict, Any, List, Tuple

import networkx as nx
from pygraphblas import Matrix, BOOL

__all__ = [
    "BooleanMatrixGraph",
    "bmg_from_nx_graph",
]


class BooleanMatrixGraph:
    """A Labeled Graph decomposed into Boolean Matrices class"""

    def __init__(self, number_of_nodes: int = 0):
        self._matrices: Dict[str, Matrix] = dict()
        self._matrices_size: int = number_of_nodes

    def __getitem__(self, label: str) -> Matrix:
        if label not in self._matrices:
            raise KeyError(f"{label}")
        return self._matrices[label]

    def __setitem__(self, label: str, matrix: Matrix):
        self._matrices[label] = matrix

    def __contains__(self, label: str) -> bool:
        return label in self._matrices

    @property
    def matrices_size(self) -> int:
        """The number of vertices in the graph

        Returns
        -------
        matrices_size: int
            Matrices size
        """
        return self._matrices_size

    def add_edge(self, u: int, v: int, label: str):
        """Add an edge between `u` and `v` with label `label`.

        The nodes u and v will be automatically added if they are
        not already in the graph.

        Parameters
        ----------
        u: int
            The tail of the edge

        v: int
            The head of the edge

        label:
            The label of the edge
        """
        if min(u, v) > self._matrices_size:
            for label in self._matrices:
                self._matrices_size = max(u, v)
                self._matrices[label].resize(self._matrices_size, self._matrices_size)

        if label not in self._matrices:
            self._matrices[label] = Matrix.sparse(
                typ=BOOL, nrows=self._matrices_size, ncols=self._matrices_size
            )

        self._matrices[label][u, v] = True


def bmg_from_nx_graph(graph: nx.MultiDiGraph) -> Tuple[BooleanMatrixGraph, List[Any]]:
    """Create a BooleanMatrixGraph from NetworkX MultiDiGraph

    Parameters
    ----------
    graph: nx.MultiDiGraph
        NetworkX MultiDiGraph

    Returns
    -------
    (nodes_mapping, g): Tuple[List[Any], BooleanMatrixGraph]
        `g` - BooleanMatrixGraph constructed according to `graph`
        `nodes_mapping` - mapping a number to a `graph` node

    Notes
    -----
    Each edge of the `graph` is expected to have a "label" attribute
    """
    g = BooleanMatrixGraph(graph.number_of_nodes())

    nodes_dict = dict()
    nodes_list = []
    nodes_num = 0

    for node in graph:
        if node not in nodes_dict:
            nodes_dict[node] = nodes_num
            nodes_num += 1
            nodes_list.append(node)

    for u, v, edge in graph.edges(data=True):
        u = nodes_dict[u]
        v = nodes_dict[v]
        label = edge["label"]

        g.add_edge(u, v, label)

    return g, nodes_list
