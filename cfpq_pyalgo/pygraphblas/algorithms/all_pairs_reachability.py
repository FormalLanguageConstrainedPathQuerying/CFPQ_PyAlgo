from pygraphblas import BOOL

from cfpq_pyalgo.classes import CNF
from cfpq_pyalgo.pygraphblas import BooleanMatrixGraph

__all__ = [
    "all_pairs_reachability_matrix",
]


def all_pairs_reachability_matrix(graph: BooleanMatrixGraph, grammar: CNF):
    m = BooleanMatrixGraph(graph.matrices_size)
    for l, r in grammar.unary_productions:
        m[l] += graph[r]

    changed = True
    while changed:
        changed = False
        for l, r1, r2 in grammar.double_productions:
            old_nnz = m[l].nvals
            m[l] += m[r1].mxm(m[r2], semiring=BOOL.LOR_LAND)
            new_nnz = m[l].nvals

            if old_nnz != new_nnz:
                changed = True

    return m[grammar.start_symbol]
