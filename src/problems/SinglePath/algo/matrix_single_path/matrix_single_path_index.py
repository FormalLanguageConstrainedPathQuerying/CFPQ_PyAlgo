from pathlib import Path

from src.problems.SinglePath.SinglePath import SinglePathProblem
from src.problems.SinglePath.algo.matrix_single_path.matrix_single_path import MatrixSinglePath

from src.graph.index_graph import IndexGraph, INDEXTYPE
from src.grammar.cnf_grammar import CnfGrammar


class MatrixSinglePathAlgo(SinglePathProblem):

    def prepare(self, graph: Path, grammar: Path):
        self.graph = IndexGraph.from_txt(graph.rename(graph.with_suffix(".txt")))
        self.grammar = CnfGrammar.from_cnf(grammar.rename(grammar.with_suffix(".cnf")))

    def solve(self):
        IndexType_monoid = INDEXTYPE.new_monoid(INDEXTYPE.PLUS, INDEXTYPE.one)
        IndexType_semiring = INDEXTYPE.new_semiring(IndexType_monoid, INDEXTYPE.TIMES)
        with IndexType_semiring, INDEXTYPE.PLUS:
            m = IndexGraph(self.graph.matrices_size)
            for l, r in self.grammar.simple_rules:
                m[l] += self.graph[r]

            changed = True
            while changed:
                changed = False
                for l, r1, r2 in self.grammar.complex_rules:
                    old_nnz = m[l].nvals
                    m[l] += m[r1].mxm(m[r2])
                    new_nnz = m[l].nvals
                    if not old_nnz == new_nnz:
                        changed = True
            return m

    def getPath(self, v_start: int, v_finish: int, nonterminal: str):
        return MatrixSinglePath(self.graph, self.grammar).get_path(v_start, v_finish, nonterminal)
