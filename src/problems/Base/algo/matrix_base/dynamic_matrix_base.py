from pyformlang.cfg import CFG
from pygraphblas import BOOL
from pygraphblas import descriptor

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.graph import Graph
from src.graph.label_graph import LabelGraph
from src.problems.Base.Base import BaseProblem
from src.problems.utils import ResultAlgo


class DynamicMatrixBaseAlgo(BaseProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

    def solve(self):
        m = LabelGraph(self.graph.matrices_size)

        for l in self.grammar.eps_rules:
            for i in range(m.matrices_size):
                m[l][i, i] = True

        for l, r in self.grammar.simple_rules:
            m[l] += self.graph[r]

        iter = 0
        front = m

        while True:
            iter += 1
            new_front = LabelGraph(self.graph.matrices_size)

            if iter != 1:
                for l, r1, r2 in self.grammar.complex_rules:
                    new_front[l].eadd(
                        other=front[r1].mxm(m[r2], semiring=BOOL.ANY_PAIR, desc=descriptor.C, mask=m[l]),
                        desc=descriptor.C,
                        mask=front[l],
                        out=new_front[l]
                    )

                for key in front:
                    m[key] += front[key]

            for l, r1, r2 in self.grammar.complex_rules:
                new_front[l] += m[r1].mxm(front[r2], semiring=BOOL.ANY_PAIR, desc=descriptor.C, mask=m[l])

            front = new_front
            if not front.has_nnz():
                return ResultAlgo(m[self.grammar.start_nonterm], iter)

    def prepare_for_solve(self):
        pass
