"""Function that solves the All-Pairs CFL-reachability problem
using boolean matrix multiplication"""
from collections import defaultdict
from typing import List, Tuple

import networkx as nx
from pyformlang.cfg import CFG
from pygraphblas import Matrix, BOOL

from cfpq_pyalgo.pygraphblas.grammars import WCNF
from cfpq_pyalgo.pygraphblas.graphs import BooleanMatrixGraph, bmg_from_nx_graph

__all__ = [
    "matrix_all_pairs_reachability",
    "_matrix_all_pairs_reachability",
]


def matrix_all_pairs_reachability(
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

    # prepare WCNF from GFG
    wcnf = WCNF(grammar)

    # prepare BooleanMatrixGraph from nx.MultiDiGraph
    matrix_graph, nodes_mapping = bmg_from_nx_graph(graph)

    # find transitive closure for each nonterminal of `wcnf`
    res = _matrix_all_pairs_reachability(matrix_graph, wcnf)

    # convert transitive closure for `wcnf.start_variable`
    # to list of pairs of nodes of `graph`
    I, J, _ = res[wcnf.start_variable.to_text()].to_lists()
    return [(nodes_mapping[u], nodes_mapping[v]) for u, v in zip(I, J)]


def _matrix_all_pairs_reachability(
    graph: BooleanMatrixGraph, grammar: WCNF
) -> BooleanMatrixGraph:
    # Initialize matrices for variables
    t = BooleanMatrixGraph(graph.matrices_size)
    for variable in grammar.variables:
        t[variable.to_text()] = Matrix.sparse(
            BOOL, nrows=graph.matrices_size, ncols=graph.matrices_size
        )

    # 0. Variable -> Epsilon
    m_id = Matrix.identity(BOOL, nrows=graph.matrices_size, value=True)
    for rule in grammar.epsilon_productions:
        t[rule.head.to_text()] += m_id

    # 1. Variable -> Terminal
    for rule in grammar.unary_productions:
        terminal = rule.body[0].to_text()
        if terminal in graph:
            t[rule.head.to_text()] += graph[terminal]

    # 2. Transitive closure calculation
    nnz = defaultdict(int)

    changed = True
    while changed:
        changed = False
        for rule in grammar.binary_productions:
            l, r1, r2 = (
                rule.head.to_text(),
                rule.body[0].to_text(),
                rule.body[1].to_text(),
            )

            old_nnz = nnz[l]

            t[l] += t[r1].mxm(t[r2], semiring=BOOL.ANY_PAIR)

            new_nnz = t[l].nvals

            changed |= old_nnz != new_nnz

            nnz[l] = new_nnz

    return t
