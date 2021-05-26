from pyformlang.cfg import CFG
from src.graph.graph import Graph

from src.problems.SinglePath.SinglePath import SinglePathProblem
from src.problems.SinglePath.algo.matrix_single_path.matrix_single_path import MatrixSinglePath

from src.graph.index_graph import IndexGraph, SAVEMIDDLETYPE
from src.grammar.cnf_grammar import CnfGrammar
from src.problems.utils import ResultAlgo


class MatrixSingleAlgo(SinglePathProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_save_middle_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

    def solve(self):
        IndexType_monoid = SAVEMIDDLETYPE.new_monoid(SAVEMIDDLETYPE.PLUS, SAVEMIDDLETYPE.one)
        IndexType_semiring = SAVEMIDDLETYPE.new_semiring(IndexType_monoid, SAVEMIDDLETYPE.TIMES)
        with IndexType_semiring, SAVEMIDDLETYPE.PLUS:
            m = IndexGraph(self.graph.matrices_size)
            for l, r in self.grammar.simple_rules:
                m[l] += self.graph[r]

            changed = True
            iter = 0
            while changed:
                iter += 1
                changed = False
                for l, r1, r2 in self.grammar.complex_rules:
                    old_nnz = m[l].nvals
                    m[l] += m[r1].mxm(m[r2])
                    new_nnz = m[l].nvals
                    if not old_nnz == new_nnz:
                        changed = True
            self.res_m = m
            return ResultAlgo(m["S"], iter)

    def getPath(self, v_start: int, v_finish: int, nonterminal: str):
        return MatrixSinglePath(self.res_m, self.grammar).get_path(v_start, v_finish, nonterminal)