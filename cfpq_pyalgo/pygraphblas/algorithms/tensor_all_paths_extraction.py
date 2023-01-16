"""The module contains a class that allows extraction of paths with context-free constraints.
The algorithm is based on the Kronecker product for Boolean matrices.
It is worth noting that for real-world applications it is better to write your own implementation,
taking into account the specifics of the grammars used.

To do this, it is necessary to get its representation as GraphBooleanDecomposition from the original graph,
and build RSMBooleanDecomposition from the grammar. Then using the function `build_tensor_index` get
`tensor_index` matrix containing information about reachability in both graph and RSM,
which will allow to extract paths with constraints set by grammar.

>>> matrix_graph, nums_to_nodes = gbd_from_nx_graph(graph)
>>> rsm = RSMBooleanDecomposition.from_rsa(RecursiveAutomaton.from_text(grammar.to_text()))
>>> matrix_graph, tensor_index = build_tensor_index(matrix_graph, rsm)
"""
from collections import deque, namedtuple
from typing import Iterable, Tuple, Set, Hashable, List, Dict, Deque, Optional

import networkx as nx

from pyformlang.cfg import CFG
from pyformlang.rsa import RecursiveAutomaton
from pygraphblas import Matrix

from cfpq_pyalgo.pygraphblas import (
    GraphBooleanDecomposition,
    RSMBooleanDecomposition,
    gbd_from_nx_graph,
)
from cfpq_pyalgo.pygraphblas.algorithms import build_tensor_index

__all__ = [
    "TensorPathsExtractor",
]

Descriptor = namedtuple(
    "Descriptor",
    [
        "current_v",
        "finish_v",
        "stack",
        "path",
    ],
)
Edge = namedtuple(
    "Edge",
    [
        "from_v",
        "label",
        "to_v",
    ],
)


class TensorPathsExtractor:
    """A class that allows to retrieve paths with context free constraints."""

    _graph: GraphBooleanDecomposition
    _rsm: RSMBooleanDecomposition
    _tensor_index: Matrix
    _terminals: Set[str]
    _graph_size: int
    _nums_to_nodes: List[Hashable]
    _nodes_to_nums: Dict[Hashable, int]

    def __init__(
        self,
        rsm: RSMBooleanDecomposition,
        graph: GraphBooleanDecomposition,
        tensor_index: Matrix,
        nums_to_nodes: List[Hashable],
    ):
        self._rsm = rsm
        self._tensor_index = tensor_index
        self._graph = graph
        self._graph_size = graph.matrices_size
        self._terminals = rsm.labels.difference(rsm.nonterminals)
        self._nums_to_nodes = nums_to_nodes
        self._nodes_to_nums = {node: i for i, node in enumerate(nums_to_nodes)}

    def get_paths(
        self,
        start_vertex: Hashable,
        finish_vertex: Hashable,
        nonterminal: str,
        max_length: Optional[int] = None,
    ) -> Iterable[List[Tuple[Hashable, str, Hashable]]]:
        """Get all paths from `start_vertex` to `finish_vertex` that
        form a word derived from a `nonterminal`.

        Parameters
        ----------
        start_vertex: Hashable
            The start vertex of the extracting paths
        finish_vertex: Hashable
            The final vertex of the extracting paths
        nonterminal: str
            Nonterminal from which the grammar derives the words formed by the extracting paths
        max_length: Optional[int]
            Restriction on the length of the extracted paths. If `max_length` is None,
            paths of any length are extracted

        Yields
        ------
        path: List[Tuple[Hashable, str, Hashable]]
            Path in graph
        """
        if not max_length:
            max_length = -1
        else:
            if max_length <= 0:
                raise ValueError("max_length must be greater than 0 or None")
        queue_terminal: Deque[Descriptor] = deque()
        queue_nonterminal: Deque[Descriptor] = deque()
        start: int = self._nodes_to_nums[start_vertex]
        finish: int = self._nodes_to_nums[finish_vertex]

        start_state: int = self._rsm.get_start_state(nonterminal)
        for finish_state in self._rsm.get_final_states(nonterminal):
            queue_nonterminal.append(
                Descriptor(
                    current_v=start_state * self._graph_size + start,
                    finish_v=finish_state * self._graph_size + finish,
                    stack=[],
                    path=[],
                )
            )

        while queue_terminal or queue_nonterminal:
            if queue_terminal:
                current_v, to_v, stack, path = queue_terminal.popleft()
            else:
                current_v, to_v, stack, path = queue_nonterminal.popleft()
            while current_v == to_v and stack:
                current_v, to_v = stack[-1]
                stack = stack[:-1]
            else:
                if current_v == to_v:
                    yield path
            graph_i: int = current_v % self._graph_size
            rsm_i: int = current_v // self._graph_size
            if 0 < max_length < len(path):
                continue
            for k in self._tensor_index[current_v]:
                if (not self._tensor_index.get(k[0], to_v, False)) and k[0] != to_v:
                    continue
                graph_k: int = k[0] % self._graph_size
                rsm_k: int = k[0] // self._graph_size
                # Try to step on an edge with the terminal
                for term in self._terminals:
                    if self._rsm[term].get(rsm_i, rsm_k, False) and self._graph[
                        term
                    ].get(graph_i, graph_k, False):
                        queue_terminal.append(
                            Descriptor(
                                current_v=k[0],
                                finish_v=to_v,
                                stack=stack,
                                path=path
                                + [
                                    Edge(
                                        self._nums_to_nodes[graph_i],
                                        term,
                                        self._nums_to_nodes[graph_k],
                                    )
                                ],
                            )
                        )
                # Try to step on an edge with the nonterminal
                for nonterm in self._rsm.nonterminals:
                    if self._rsm[nonterm].get(rsm_i, rsm_k, False):
                        start_state: int = self._rsm.get_start_state(nonterm)
                        for finish_state in self._rsm.get_final_states(nonterm):
                            queue_nonterminal.append(
                                Descriptor(
                                    current_v=start_state * self._graph_size + graph_i,
                                    finish_v=finish_state * self._graph_size + graph_k,
                                    stack=stack + [(k[0], to_v)],
                                    path=path,
                                )
                            )

    @classmethod
    def build_path_extractor(
        cls, graph: nx.MultiDiGraph, grammar: CFG
    ) -> "TensorPathsExtractor":
        """Creates a TensorPathsExtractor that allows to extract paths from `graph` with
        constraints given by the `grammar`.

        Parameters
        ----------
        graph: nx.MultiDiGraph
            The graph from which the paths will be extracted
        grammar: CFG
            A grammar that sets context-free constraints on extracting paths

        Returns
        -------
        path_extractor: TensorPathsExtractor
            Paths extractor constructed according to `graph` and `grammar`
        """
        matrix_graph, nums_to_nodes = gbd_from_nx_graph(graph)
        rsm = RSMBooleanDecomposition.from_rsa(
            RecursiveAutomaton.from_text(grammar.to_text())
        )
        matrix_graph, tensor_index = build_tensor_index(matrix_graph, rsm)
        return cls(rsm, matrix_graph, tensor_index, nums_to_nodes)
