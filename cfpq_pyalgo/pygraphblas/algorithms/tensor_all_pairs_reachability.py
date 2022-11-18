"""Function that solves the All-Pairs CFL-reachability problem
using boolean matrix Kronecker product"""
from typing import Tuple, List

import networkx as nx

from pyformlang.cfg import CFG
from pyformlang.rsa import RecursiveAutomaton
from pygraphblas import Matrix, BOOL

from cfpq_pyalgo.pygraphblas import (
    BooleanMatrixGraph,
    BooleanMatrixRsm,
    bmg_from_nx_graph,
)


def tensor_all_pairs_reachability(
    graph: nx.MultiDiGraph, grammar: CFG
) -> List[Tuple[int, int]]:
    """Determines the pairs of vertices (u, v) where there exists a path from u to v
    in `graph` and its word is in the language of Context-Free Grammar `grammar`.

    Parameters
    ----------
    graph: `nx.MultiDiGraph`
        NetworkX MultiDiGraph

    grammar: `CFG`
        Context-free grammar

    Returns
    -------
    pairs: `List[Tuple[int, int]]`
        List of CFL-reachable vertices pairs
    """
    # if the `graph` is empty, then the answer is empty
    if graph.number_of_nodes() == 0:
        return []

    # prepare BooleanMatrixRsm from GFG
    rsm: BooleanMatrixRsm = BooleanMatrixRsm.from_rsa(
        RecursiveAutomaton.from_text(grammar.to_text())
    )

    # prepare BooleanMatrixGraph from nx.MultiDiGraph
    matrix_graph, nodes_mapping = bmg_from_nx_graph(graph)

    # find transitive closure for each nonterminal of `rsm`
    res, _ = _build_tensor_index(matrix_graph, rsm)

    # convert transitive closure for `wcnf.start_variable`
    # to list of pairs of nodes of `graph`
    I, J, _ = res[grammar.start_symbol.to_text()].to_lists()
    return [(nodes_mapping[u], nodes_mapping[v]) for u, v in zip(I, J)]


def _build_tensor_index(
    graph: BooleanMatrixGraph, rsm: BooleanMatrixRsm
) -> Tuple[BooleanMatrixGraph, Matrix]:
    graph_size = graph.matrices_size
    # Initialize matrices for all labels
    t = BooleanMatrixGraph(graph.matrices_size)
    for label in rsm.labels:
        if label in graph:
            t[label] = graph[label].dup()
        else:
            t[label] = Matrix.sparse(BOOL, graph_size, graph_size)
    # 0. Boxes with epsilon path
    diagonal = Matrix.identity(BOOL, graph_size, True)
    for nonterminal in rsm.nonterminals:
        if rsm.get_start_state(nonterminal) in rsm.get_final_states(nonterminal):
            t[nonterminal] += diagonal
    del diagonal

    # 2. CFL reachability transitive closure calculation
    kron_size = rsm.matrices_size * graph_size
    changed = True
    while changed:
        changed = False
        # 2.1 Calculation of Kronecker product and its transitive closure
        kron = Matrix.sparse(BOOL, kron_size, kron_size)
        for label in rsm.labels:
            kron += rsm[label].kronecker(t[label])
        _transitive_closure(kron)
        # 2.2 Update graph
        for nonterminal in rsm.nonterminals:
            start_state = rsm.get_start_state(nonterminal)
            block = Matrix.sparse(BOOL, graph_size, graph_size)
            for final_state in rsm.get_final_states(nonterminal):
                start_i = start_state * graph_size
                start_j = final_state * graph_size
                block += kron[
                    start_i : start_i + graph_size - 1,
                    start_j : start_j + graph_size - 1,
                ]
            control_sum = t[nonterminal].nvals
            t[nonterminal] += block
            new_control_sum = t[nonterminal].nvals
            if new_control_sum != control_sum:
                changed = True
    return t, kron


def _transitive_closure(m: Matrix):
    prev = m.nvals
    degree = m
    with BOOL.ANY_PAIR:
        degree = degree @ m
        m += degree
    while prev != m.nvals:
        prev = m.nvals
        with BOOL.ANY_PAIR:
            degree = degree @ m
            m += degree
