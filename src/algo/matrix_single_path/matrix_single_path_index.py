from pathlib import Path

from src.algo.algo_interface import CFPQAlgo

from src.graph.index_graph import IndexGraph, INDEXTYPE
from src.grammar.cnf_grammar import CnfGrammar


class MatrixSinglePathSolver(CFPQAlgo):
    def __init__(self, path_to_graph: Path, path_to_grammar: Path):
        super().__init__(path_to_graph, path_to_grammar)
        self.graph = IndexGraph.from_txt(str(path_to_graph) + ".txt")
        self.grammar = CnfGrammar.from_cnf(str(path_to_grammar) + ".cnf")

    def solve(self):
        pass


class MatrixSinglePathAlgo(MatrixSinglePathSolver):
    def solve(self):
        IndexType_monoid = INDEXTYPE.new_monoid(INDEXTYPE.PLUS, INDEXTYPE.one)
        IndexType_semiring = INDEXTYPE.new_semiring(IndexType_monoid, INDEXTYPE.TIMES)
        with IndexType_semiring, INDEXTYPE.PLUS:
            m = IndexGraph()
            for l, r in self.grammar.simple_rules:
                m[l] += self.graph[r]
            changed = True
            while changed:
                changed = False
                for l, r1, r2 in self.grammar.complex_rules:
                    old_nnz = m[l].nvals
                    m[l] += m[r1] @ m[r2]
                    new_nnz = m[l].nvals
                    if not old_nnz == new_nnz:
                        changed = True
            return m
