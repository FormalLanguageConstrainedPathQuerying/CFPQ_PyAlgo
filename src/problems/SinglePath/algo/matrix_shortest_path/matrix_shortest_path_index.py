from pyformlang.cfg import CFG
from src.graph.graph import Graph

from pygraphblas import Matrix

from src.problems.SinglePath.SinglePath import SinglePathProblem
from src.problems.SinglePath.algo.matrix_shortest_path.matrix_shortest_path import MatrixShortestPath

from src.graph.length_graph import LengthGraph, SAVELENGTHTYPE
from src.grammar.cnf_grammar import CnfGrammar
from src.problems.utils import ResultAlgo


class MatrixShortestAlgo(SinglePathProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_save_length_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

    def solve(self):
        IndexType_monoid = SAVELENGTHTYPE.new_monoid(SAVELENGTHTYPE.PLUS, SAVELENGTHTYPE.one)
        IndexType_semiring = SAVELENGTHTYPE.new_semiring(IndexType_monoid, SAVELENGTHTYPE.TIMES)
        with IndexType_semiring, SAVELENGTHTYPE.PLUS:
            m = LengthGraph(self.graph.matrices_size)
            for l, r in self.grammar.simple_rules:
                m[l] += self.graph[r]

            iter = 0
            changed_nonterms = self.grammar.nonterms
            while len(changed_nonterms) > 0:
                iter += 1
                new_changes = set()
                for l, r1, r2 in self.grammar.complex_rules:
                    if r1 in changed_nonterms or r2 in changed_nonterms:
                        old_m = m[l].dup()
                        old_nnz = m[l].nvals
                        m[l] += m[r1].mxm(m[r2])
                        new_nnz = m[l].nvals
                        if not old_nnz == new_nnz:
                            new_changes.add(l)
                        elif new_nnz > 0:
                            C = m[l].emult(old_m, SAVELENGTHTYPE.SUBTRACTION)
                            if C.nonzero().nvals > 0:
                                new_changes.add(l)
                changed_nonterms = new_changes
            self.res_m = m
            return ResultAlgo(m[self.grammar.start_nonterm], iter)

    def prepare_for_solve(self):
        pass

    def getPath(self, v_start: int, v_finish: int, nonterminal: str):
        return MatrixShortestPath(self.res_m, self.grammar).get_path(v_start, v_finish, nonterminal)