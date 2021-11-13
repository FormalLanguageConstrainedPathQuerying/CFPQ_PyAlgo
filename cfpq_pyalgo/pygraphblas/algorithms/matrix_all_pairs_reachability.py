"""Function that solves the all-pairs CFL-reachability problem using boolean matrix multiplication"""
from typing import List, Tuple

import networkx as nx
from pygraphblas import Matrix, BOOL
from pyformlang.cfg import CFG
from cfpq_pyalgo.pygraphblas import WCNF, BooleanMatrixGraph

__all__ = [
    "matrix_all_pairs_reachability",
]


def matrix_all_pairs_reachability(
    graph: nx.MultiDiGraph, grammar: CFG
) -> List[Tuple[int, int]]:
    """Determines the pairs of vertices (u, v) where there exists a path from u to v in ``graph`` and its word
    is in the language of ``grammar``.

    Parameters
    ----------
    graph: `nx.MultiDiGraph`
        NetworkX MultiDiGraph
    grammar: `CFG`
        Context-free grammar

    Returns
    -------
    `List`[`Tuple`[`int`, `int`]]
        List of CFL-reachable vertices pairs
    """

    # prepare WCNF from GFG
    wcnf = WCNF(grammar)

    # prepare BooleanMatrixGraph from nx.MultiDiGraph
    matrix_graph = BooleanMatrixGraph.from_nx_graph(graph)
    if matrix_graph.matrices_size == 0:
        return []

    # find transitive closure for each nonterminal
    res: BooleanMatrixGraph = _matrix_all_pairs_reachability(matrix_graph, wcnf)

    # convert transitive closure for start nonterminal to list of pairs
    res_lists = res[wcnf.start_symbol.to_text()].to_lists()
    return [(int(v), int(to)) for v, to in zip(res_lists[0], res_lists[1])]


def _matrix_all_pairs_reachability(
    graph: BooleanMatrixGraph, grammar: WCNF
) -> BooleanMatrixGraph:
    # Initialize matrices for nonterminals
    t = BooleanMatrixGraph(graph.matrices_size)
    for n in grammar.variables:
        t[n.to_text()] = Matrix.sparse(
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
    changed = True
    while changed:
        changed = False
        for rule in grammar.binary_productions:
            l, r1, r2 = (
                rule.head.to_text(),
                rule.body[0].to_text(),
                rule.body[1].to_text(),
            )
            old_nnz = t[l].nvals
            t[l] += t[r1].mxm(t[r2], semiring=BOOL.ANY_PAIR)
            new_nnz = t[l].nvals
            changed |= old_nnz != new_nnz

    return t
