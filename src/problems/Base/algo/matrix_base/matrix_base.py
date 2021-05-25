from pygraphblas import BOOL
from pyformlang.cfg import CFG
from src.graph.graph import Graph

from src.problems.Base.Base import BaseProblem

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.problems.utils import ResultAlgo


class MatrixBaseAlgo(BaseProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph.load_bool_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

    def solve(self):
        m = LabelGraph(self.graph.matrices_size)
        for l, r in self.grammar.simple_rules:
            m[l] += self.graph[r]

        changed = True
        iter = 0
        while changed:
            iter += 1
            changed = False
            for l, r1, r2 in self.grammar.complex_rules:
                old_nnz = m[l].nvals
                m[l] += m[r1].mxm(m[r2], semiring=BOOL.LOR_LAND)
                new_nnz = m[l].nvals
                changed |= not old_nnz == new_nnz
        return ResultAlgo(m[self.grammar.start_nonterm], iter)
