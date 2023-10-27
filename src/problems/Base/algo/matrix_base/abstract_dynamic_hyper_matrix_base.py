from abc import ABC, abstractmethod
from collections import defaultdict
from time import time
from typing import Optional

from line_profiler import LineProfiler
from pyformlang.cfg import CFG
from graphblas.core.matrix import Matrix, Vector
from graphblas.core.dtypes import BOOL
from graphblas.semiring import any_pair
import graphblas.monoid

from src.grammar.cnf_grammar import CnfGrammar
from src.grammar.hyper_cnf_grammar import HyperCnfGrammar
from src.graph.graph import Graph
from src.matrix.enhanced_matrix import EnhancedMatrix
from src.matrix.hyper_matrix_space import HyperVectorOrientation, HyperMatrixSpace
from src.matrix.matrix_to_enhanced_adapter import MatrixToEnhancedAdapter
from src.matrix.hyper_square_matrix_space import HyperSquareMatrixSpace
from src.matrix.short_circuiting_for_empty_matrix import ShortCircuitingForEmptyMatrix
from src.problems.Base.Base import BaseProblem
from src.problems.utils import ResultAlgo
from src.utils.default_dict import DefaultKeyDependentDict

from src.utils.unique_ptr import unique_ptr

DOMAIN = BOOL
SEMIRING = any_pair
MONOID = graphblas.monoid.any


class AbstractDynamicHyperMatrixBaseAlgo(BaseProblem, ABC):
    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_python_graphblas_bool_graph()
        # TODO weak cnf?
        self.grammar = CnfGrammar.from_cfg(grammar)
        self.hyper_grammar = HyperCnfGrammar.from_cnf(self.grammar)
        self.profiler: Optional[LineProfiler] = None

    def inject_cnf_grammar(self, grammar: CnfGrammar):
        self.grammar = grammar
        self.hyper_grammar = HyperCnfGrammar.from_cnf(self.grammar)

    def inject_hyper_cnf_grammar(self, grammar: HyperCnfGrammar):
        self.hyper_grammar = grammar

    def inject_profiler(self, profiler):
        self.profiler = profiler

    def solve(self):
        self.hyper_nonterm_size = self.hyper_grammar.get_hyper_nonterm_size(self.graph.matrices.keys())
        print("hyper_nonterm_size:", self.hyper_nonterm_size)

        self.hyper_space: HyperMatrixSpace = HyperSquareMatrixSpace(
            n=self.graph.matrices_size,
            hyper_size=self.hyper_nonterm_size
        )

        self._analyze_complex_rules()

        front = self._create_front()

        # if self.profiler is not None:
        #     self.profiler.add_function(FormatOptimizedMatrix.mxm)
        #     self.profiler.add_function(IAddOptimizedMatrix._map_and_fold)
        #     self.profiler.add_function(IAddOptimizedMatrix.iadd)

        m = DefaultKeyDependentDict(self._create_enhanced_matrix_for_var)
        for key in front:
            m[key] += front[key]
        iter = 0

        stats = defaultdict(lambda: 0)

        t_last_iter = time()
        while True:
            iter += 1
            print(iter, "m:", sum(v.nvals for v in m.values()), "f:", sum(v.nvals for v in front.values()),  time() - t_last_iter)
            t_last_iter = time()
            # print("-------", iter, "-------")
            #
            # for (k, v) in m.items():
            #     print(k)
            #     print(str(v))
            #     print()
            #     print("----------------------")
            #     print()

            new_front = DefaultKeyDependentDict(lambda var_name: (
                self.hyper_space.create_hyper_vector(DOMAIN, HyperVectorOrientation.VERTICAL)
                if var_name in self.hyper_grammar.hyper_nonterms
                else unique_ptr(Matrix(DOMAIN, self.graph.matrices_size, self.graph.matrices_size))
            ))

            if iter != 1:
                for l, r1, r2 in self.hyper_grammar.complex_rules:
                    t0 = time()
                    if m[r1].nvals != 0 and front[r2].nvals != 0:
                        mxm = m[r1].mxm(front[r2], op=SEMIRING)
                        if mxm.nvals != 0:
                            mxm = self._fix_hyper_vector(mxm, reduce=l not in self.hyper_grammar.hyper_nonterms)
                            new_front[l] << new_front[l].ewise_add(mxm)
                    stats[("mxm", l, r1, r2)] += time() - t0
                for key in front:
                    t0 = time()
                    m[key] += front[key]
                    stats["+=", key] += time() - t0

            for l, r1, r2 in self.hyper_grammar.complex_rules:
                t0 = time()
                if m[r2].nvals != 0 and front[r1].nvals != 0:
                    mxm = m[r2].rmxm(front[r1], op=SEMIRING)
                    if mxm.nvals != 0:
                        mxm = self._fix_hyper_vector(mxm, reduce=l not in self.hyper_grammar.hyper_nonterms)
                        new_front[l] << new_front[l].ewise_add(mxm)
                stats[("rmxm", l, r1, r2)] += time() - t0

            front = new_front
            for key in front:
                t0 = time()
                front[key] = m[key].r_complimentary_mask(front[key])
                stats[("mask", key)] += time() - t0

            if all(v.nvals == 0 for v in front.values()):
                print("M:", sum(v.nvals for v in m.values()))
                for k, v in m.items():
                    print(k, " -- ", v.nvals)
                    # print([v2.nvals for v2 in v.base.base.matrices])
                for k, v in sorted(stats.items(), key=lambda it: it[1]):
                    print(k, " -- ", v)
                # m_out = Matrix(DOMAIN, self.graph.matrices_size, self.graph.matrices_size)
                # zero = Matrix(DOMAIN, nrows=self.graph.matrices_size, ncols=self.graph.matrices_size)
                # mask = Vector.from_scalar(True, size=self.graph.matrices_size, dtype=DOMAIN).diag()
                # m_out(~mask.S) << matrix_S.ewise_add(zero, op=graphblas.monoid.any)
                # print("c mask:", m_out.nvals)
                return ResultAlgo(m[self.hyper_grammar.start_nonterm].to_matrix(), iter)

    def _create_front(self):
        front = DefaultKeyDependentDict(self._create_matrix_for_front)
        for l in self.hyper_grammar.eps_rules:
            front[l] = Vector.from_scalar(True, size=self.graph.matrices_size, dtype=DOMAIN).diag()
        for l, r in self.hyper_grammar.simple_rules:
            front[l] << front[l].ewise_add(self.graph[r], op=MONOID)
        for rule in self.hyper_grammar.hyper_simple_rules:
            front[rule.nonterm] << front[rule.nonterm].ewise_add(self.hyper_space.stack_into_hyper_column([
                self.graph[label]
                for label in (
                    f"{rule.term_prefix}{str(i)}{rule.term_suffix}"
                    for i in range(self.hyper_nonterm_size)
                )
            ]), op=MONOID)
        return front

    def _analyze_complex_rules(self):
        self.r1s_with_hyper_r2 = set()
        self.r1s_with_non_hyper_r2 = set()
        self.r2s_with_hyper_r1 = set()
        self.r2s_with_non_hyper_r1 = set()
        for _, r1, r2 in self.hyper_grammar.complex_rules:
            (self.r1s_with_hyper_r2 if r2 in self.hyper_grammar.hyper_nonterms else self.r1s_with_non_hyper_r2).add(r1)
            (self.r2s_with_hyper_r1 if r1 in self.hyper_grammar.hyper_nonterms else self.r2s_with_non_hyper_r1).add(r2)

    def _create_enhanced_matrix_for_var(self, var_name: str) -> EnhancedMatrix:
        if var_name in self.hyper_grammar.hyper_nonterms:
            base_matrix = self.hyper_space.create_hyper_vector(
                DOMAIN,
                HyperVectorOrientation.VERTICAL
                if var_name in self.r2s_with_hyper_r1 or var_name in self.r1s_with_non_hyper_r2
                else HyperVectorOrientation.HORIZONTAL
            )
        else:
            base_matrix = unique_ptr(Matrix(DOMAIN, self.graph.matrices_size, self.graph.matrices_size))

        return self.hyper_space.wrap_enhanced_hyper_matrix(
            self.non_hyper_enhance_matrix(
                ShortCircuitingForEmptyMatrix(
                    MatrixToEnhancedAdapter(base_matrix)
                ),
                var_name
            )
        )

    @abstractmethod
    def non_hyper_enhance_matrix(self, base_matrix: EnhancedMatrix, var_name: str) -> EnhancedMatrix:
        pass

    def _create_matrix_for_front(self, var_name: str) -> Matrix:
        return (
            self.hyper_space.create_hyper_vector(DOMAIN, HyperVectorOrientation.VERTICAL)
            if var_name in self.hyper_grammar.hyper_nonterms
            else unique_ptr(Matrix(DOMAIN, self.graph.matrices_size, self.graph.matrices_size))
        )

    def _fix_hyper_vector(self, hyper_vector: Matrix, reduce: bool) -> Matrix:
        return self.hyper_space.reduce_hyper_vector_or_cell(hyper_vector) if reduce else self.hyper_space.hyper_rotate(
            hyper_vector, HyperVectorOrientation.VERTICAL)

    def prepare_for_solve(self):
        pass
