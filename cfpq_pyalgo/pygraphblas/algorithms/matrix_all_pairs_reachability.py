"""Function that solves the All-Pairs CFL-reachability problem
using boolean matrix multiplication."""
from collections import defaultdict
from typing import Set, Tuple, Hashable

import networkx as nx
from pyformlang.cfg import CFG
from pygraphblas import Matrix, BOOL

from cfpq_pyalgo.pygraphblas.grammars import WCNF
from cfpq_pyalgo.pygraphblas.graphs import GraphBooleanDecomposition, gbd_from_nx_graph

__all__ = [
    "matrix_all_pairs_reachability",
    "_matrix_all_pairs_reachability",
]


def matrix_all_pairs_reachability(
    graph: nx.MultiDiGraph, grammar: CFG
) -> Set[Tuple[Hashable, Hashable]]:
    """Determines the set of vertex pairs (u, v) in `graph` such that there is a path from u to v
    whose edge labels form a word from the language generated by the context-free grammar `grammar`.

    Parameters
    ----------
    graph: `nx.MultiDiGraph`
        NetworkX MultiDiGraph

    grammar: `CFG`
        Context-free grammar

    Returns
    -------
    pairs: `Set[Tuple[Hashable, Hashable]]`
        Set of CFL-reachable vertices pairs
    """
    # if the `graph` is empty, then the answer is empty
    if graph.number_of_nodes() == 0:
        return set()

    # prepare WCNF from GFG
    wcnf = WCNF(grammar)

    # prepare GraphBooleanDecomposition from nx.MultiDiGraph
    matrix_graph, nodes_mapping = gbd_from_nx_graph(graph)

    # find transitive closure for each nonterminal of `wcnf`
    res = _matrix_all_pairs_reachability(matrix_graph, wcnf)

    # convert transitive closure for `wcnf.start_variable`
    # to set of pairs of nodes of `graph`
    I, J, _ = res[wcnf.start_variable.to_text()].to_lists()
    return set((nodes_mapping[u], nodes_mapping[v]) for u, v in zip(I, J))


def _matrix_all_pairs_reachability(
    graph: GraphBooleanDecomposition, grammar: WCNF
) -> GraphBooleanDecomposition:
    # Initialize matrices for variables
    t = GraphBooleanDecomposition(graph.matrices_size)
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

            t[l] += t[r1].mxm(t[r2], semiring=BOOL.ANY_PAIR)

            new_nnz = t[l].nvals

            changed |= nnz[l] != new_nnz

            nnz[l] = new_nnz

    return t
