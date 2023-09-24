from time import time

from pyformlang.cfg import CFG
from pygraphblas import BOOL, Matrix
from pygraphblas import descriptor

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.graph import Graph
from src.graph.label_graph import LabelGraph
from src.problems.Base.Base import BaseProblem
from src.problems.Base.algo.matrix_base.accum_matrix import AccumMatrix
from src.problems.utils import ResultAlgo

MIN_SIZE = 10
BASE = 10


class DynamicMatrixBaseAlgo(BaseProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

    def solve(self):
        t0 = time()

        front = LabelGraph(self.graph.matrices_size)

        for l in self.grammar.eps_rules:
            for i in range(front.matrices_size):
                front[l][i, i] = True

        for l, r in self.grammar.simple_rules:
            front[l] += self.graph[r]

        print("init front", time() - t0)

        # print("front:", [(x.format, x.nvals) for x in front.matrices.values()])

        t0 = time()

        m0 = LabelGraph(self.graph.matrices_size, elm_factory=lambda _: AccumMatrix(BASE, MIN_SIZE))
        m1 = LabelGraph(self.graph.matrices_size, elm_factory=lambda _: AccumMatrix(BASE, MIN_SIZE, format=1))
        for key in front:
            m0[key] += front[key].dup()
            tmp = front[key].dup()
            tmp.format = 1
            m1[key] += tmp

        iter = 0
        zero = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)

        reformat1 = 0
        mult1 = 0
        add = 0
        reformat2 = 0
        mult2 = 0
        mask = 0

        print("init m1 and m2", time() - t0)

        # print("m0:", [(x.format, x.nvals, k) for k in m0 for x in m0[k].matrices])
        # print("m1:", [(x.format, x.nvals, k) for k in m1 for x in m1[k].matrices])

        while True:
            iter += 1
            print("Iter:", iter, "at", time())
            print("\tm0:", m0.nvals(), "front:", front.nvals(), "ratio:", front.nvals() / m0.nvals())
            new_front = LabelGraph(self.graph.matrices_size)

            t0 = time()
            front.do_format(1)
            new_front.do_format(1)
            print("\tReformat1:", time() - t0)
            reformat1 += time() - t0

            t0 = time()
            n1 = 0
            n2 = 0
            n3 = 0
            if iter != 1:
                for l, r1, r2 in self.grammar.complex_rules:
                    if m1[r1].nvals != 0 and front[r2].nvals != 0:
                        n1 += m1[r1].nvals
                        n2 += front[r2].nvals
                        mxm = m1[r1].map_and_fold(fmap=lambda it: it.mxm(front[r2], semiring=BOOL.ANY_PAIR))
                        n3 += mxm.nvals
                        new_front[l] += mxm

                print("\tMult1:", time() - t0, n1, n2, n3)
                mult1 += time() - t0

                t0 = time()
                # print("front:", [(x.format, x.nvals) for x in front.matrices.values()])
                # print("m1:", [(x.format, x.nvals, k) for k in m1 for x in m1[k].matrices])
                for key in front:
                    if front[key].nvals != 0:
                        # print("front[key]:", (front[key].format, front[key].nvals))
                        m1[key] += front[key]
                # if any(x.format == 0 for k in m1 for x in m1[k].matrices):
                #     print("m1:", [(x.format, x.nvals, k) for k in m1 for x in m1[k].matrices])
                #     d = 0
                print("\tAdd:", time() - t0)
                add += time() - t0

                t0 = time()
                front.do_format(0)
                new_front.do_format(0)
                print("\tReformat2:", time() - t0)
                reformat2 += time() - t0

                t0 = time()
                for key in front:
                    if front[key].nvals != 0:
                        m0[key] += front[key]
                print("\tAdd:", time() - t0)
                add += time() - t0

            else:

                t0 = time()
                front.do_format(0)
                new_front.do_format(0)
                print("\tReformat2:", time() - t0)
                reformat2 += time() - t0

            t0 = time()
            n1 = 0
            n2 = 0
            n3 = 0
            n4 = 0
            for l, r1, r2 in self.grammar.complex_rules:
                if front[r1].nvals != 0 and m0[r2].nvals != 0:
                    n1 += front[r1].nvals
                    n2 += m0[r2].nvals
                    mxm = m0[r2].map_and_fold(fmap=lambda it: front[r1].mxm(it, semiring=BOOL.ANY_PAIR))
                    n3 += mxm.nvals
                    new_front[l] += mxm

            print("\tMult2:", time() - t0, n1, n2, n3)
            mult2 += time() - t0

            t0 = time()

            front = new_front
            for key in front:
                for m in m0[key].matrices:
                    front[key] = front[key].eadd(zero, mask=m, desc=descriptor.C)

            print("\tMask:", time() - t0)
            mask += time() - t0

            if not front.has_nnz():
                print("reformat1:", reformat1)
                print("mult1:", mult1)
                print("add:", add)
                print("reformat2:", reformat2)
                print("mult2:", mult2)
                print("mask:", mask)
                # print("m0:", [(x.format, x.nvals, k) for k in m0 for x in m0[k].matrices])
                # print("m1:", [(x.format, x.nvals, k) for k in m1 for x in m1[k].matrices])
                return ResultAlgo(m0[self.grammar.start_nonterm].map_and_fold(), iter)

    def prepare_for_solve(self):
        pass
