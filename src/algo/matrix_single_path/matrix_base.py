from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph


def matrix_base_algo(g: LabelGraph, grammar: CnfGrammar):
    m = LabelGraph(g.matrices_size)
    for l, r in grammar.simple_rules:
        m[l] += g[r]
    changed = True
    while changed:
        changed = False
        for l, r1, r2 in grammar.complex_rules:
            old_nnz = m[l].nvals
            m[l] += m[r1] @ m[r2]
            new_nnz = m[l].nvals
            changed |= not old_nnz == new_nnz
    return m[grammar.start_nonterm]
