from time import time

from pyformlang.cfg import CFG
from pygraphblas import BOOL, Matrix

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.graph import Graph
from src.graph.label_graph import LabelGraph
from src.matrix.iadd_optimized_matrix import IAddOptimizedMatrix
from src.matrix.format_optimized_matrix import FormatOptimizedMatrix
from src.problems.Base.Base import BaseProblem
from src.problems.utils import ResultAlgo

MIN_SIZE = 10
BASE = 10


class DynamicMatrixBaseAlgo(BaseProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

    def inject_cnf_grammar(self, grammar: CnfGrammar):
        self.grammar = grammar

    def solve(self):
        front = LabelGraph(self.graph.matrices_size)

        for l in self.grammar.eps_rules:
            for i in range(front.matrices_size):
                front[l][i, i] = True

        for l, r in self.grammar.simple_rules:
            front[l] += self.graph[r]

        m = LabelGraph(self.graph.matrices_size, elm_factory=lambda _: FormatOptimizedMatrix(
            FormatOptimizedMatrix(
                IAddOptimizedMatrix(
                    Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
                )
            )
        ))
        for key in front:
            m[key] += front[key]

        iter = 0

        while True:
            iter += 1
            print("Iter:", iter, "at", time())
            print("\tm0:", m.nvals(), "front:", front.nvals(), "ratio:", front.nvals() / m.nvals())

            # al_ld_r = 0
            # for (l, r1, r2) in self.grammar.complex_rules:
            #     if r2.startswith("VAR:load_") and r2.endswith("_r#CNF#"):
            #         al_ld_r += front[l].nvals
            # print("Al_ld_r:", al_ld_r)

            new_front = LabelGraph(self.graph.matrices_size)

            t0 = time()
            n1 = 0
            n2 = 0
            n3 = 0
            if iter != 1:
                for l, r1, r2 in self.grammar.complex_rules:
                    if m[r1].nvals != 0 and front[r2].nvals != 0:
                        n1 += m[r1].nvals
                        n2 += front[r2].nvals
                        mxm = m[r1].mxm(front[r2], semiring=BOOL.ANY_PAIR)
                        n3 += mxm.nvals
                        # if l == "FTh":
                        #     print("FTh1:", r1, r2, ":", m[r1].nvals, front[r2].nvals, mxm.nvals)
                        new_front[l] += mxm

                print("\tMult1:", time() - t0, n1, n2, n3)

                t0 = time()
                for key in front:
                    if front[key].nvals != 0:
                        m[key] += front[key]
                print("\tAdd:", time() - t0)

            t0 = time()
            n1 = 0
            n2 = 0
            n3 = 0
            for l, r1, r2 in self.grammar.complex_rules:
                if front[r1].nvals != 0 and m[r2].nvals != 0:
                    n1 += front[r1].nvals
                    n2 += m[r2].nvals
                    mxm = m[r2].rmxm(front[r1], semiring=BOOL.ANY_PAIR)
                    n3 += mxm.nvals
                    # if l == "FTh":
                    #     print("FTh2:", front[r1].nvals, m[r2].nvals, mxm.nvals)
                    new_front[l] += mxm

            print("\tMult2:", time() - t0, n1, n2, n3)

            t0 = time()

            front = new_front

            print("Al", new_front["Al"].nvals)
            print("PT", new_front["PT"].nvals)
            print("PTh", new_front["PTh"].nvals)
            print("FT", new_front["FT"].nvals)
            print("FTh", new_front["FTh"].nvals)

            for key in front:
                front[key] = m[key].r_complimentary_mask(front[key])

            print("\tMask:", time() - t0)

            if not front.has_nnz():
                return ResultAlgo(m[self.grammar.start_nonterm].to_matrix(), iter)

    def prepare_for_solve(self):
        pass
