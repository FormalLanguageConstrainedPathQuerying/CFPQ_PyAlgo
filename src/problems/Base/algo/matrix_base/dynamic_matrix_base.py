import gc
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
from src.grammar.java_points_to_analysis import create_java_points_to_hyper_grammar
from src.graph.graph import Graph
from src.matrix.enhanced_matrix import OPTIMIZE_EMPTY, EnhancedMatrix
from src.matrix.hyper_matrix_space import HyperVectorOrientation, HyperMatrixSpace
from src.matrix.iadd_optimized_matrix import IAddOptimizedMatrix
from src.matrix.format_optimized_matrix import FormatOptimizedMatrix
from src.matrix.matrix_to_enhanced_adapter import MatrixToEnhancedAdapter
from src.matrix.hyper_square_matrix_space import HyperSquareMatrixSpace
from src.problems.Base.Base import BaseProblem
from src.problems.utils import ResultAlgo
from src.utils.default_dict import DefaultKeyDependentDict
from src.utils.time_profiler import SimpleTimer

from src.utils.unique_ptr import unique_ptr

DOMAIN = BOOL
SEMIRING = any_pair


class DynamicMatrixBasAlgo(BaseProblem):
    def prepare(self, graph: Graph, grammar: CFG):
        # print_memory_use_in_kb("before prepare")
        self.graph = graph
        self.graph.load_python_graphblas_bool_graph()
        # TODO weak cnf?
        self.grammar = CnfGrammar.from_cfg(grammar)
        self.profiler: Optional[LineProfiler] = None
        # print_memory_use_in_kb("after prepare")

    def inject_cnf_grammar(self, grammar: CnfGrammar):
        self.grammar = grammar

    def inject_profiler(self, profiler):
        self.profiler = profiler

    def solve(self):
        t_start = time()
        gc.set_threshold(1, 10, 10)
        # print("gc.get_threshold():", gc.get_threshold())
        # print("gc.isenabled():", gc.isenabled())
        t0 = time()
        if self.grammar.start_nonterm == "PT":
            self.hyper_grammar = create_java_points_to_hyper_grammar(graph_labels=self.graph.matrices.keys())
        else:
            self.hyper_grammar = HyperCnfGrammar.from_cnf(self.grammar)

        self.hyper_space: HyperMatrixSpace = HyperSquareMatrixSpace(
            n=self.graph.matrices_size,
            hyper_size=self.hyper_grammar.hyper_nonterm_size
        )

        self._analyze_complex_rules()

        # print_memory_use_in_kb("before front")
        front = self._create_front()
        # print_memory_use_in_kb("after front")

        if self.profiler is not None:
            self.profiler.add_function(FormatOptimizedMatrix.mxm)
            self.profiler.add_function(IAddOptimizedMatrix._map_and_fold)
            self.profiler.add_function(IAddOptimizedMatrix.iadd)
        #     self.profiler.add_function(self._fix_hyper_vector)
        #     self.profiler.add_function(HyperMatrixUtils.hyper_row_to_hyper_column)
        #     self.profiler.add_function(HyperMatrixUtils.hyper_column_to_hyper_row)
        #     self.profiler.add_function(HyperMatrixUtils.hyper_column_to_hyper_matrix)
        #     self.profiler.add_function(HyperMatrixUtils.reduce_hyper_row)
        #     self.profiler.add_function(HyperMatrixUtils.reduce_hyper_column)
        #     self.profiler.add_function(HyperSquareMatrixSpace.hyper_rotate)
        #     self.profiler.add_function(HyperSquareMatrixSpace.to_block_diag_matrix)

        # self.profiler.add_function(HyperSquareMatrixSpace.to_block_diag_matrix)
        # self.profiler.add_function(HyperSquareMatrixSpace.to_small_block_diag_matrix)
        #     self.profiler.add_function(HyperMatrix.mxm)
        #     self.profiler.add_function(HyperMatrix.rmxm)
        #     self.profiler.add_function(HyperMatrix.r_complimentary_mask)
        #     self.profiler.add_function(HyperMatrix.__iadd__)
        #     self.profiler.add_function(FormatOptimizedMatrix.mxm)

        m = DefaultKeyDependentDict(self._create_enhanced_matrix_for_var)
        for key in front:
            if m[key].format == 0:
                # print(0, key, "m:", m[key].nvals, "f:", front[key].nvals)
                m[key] += front[key]
            else:
                # print(1, key, "m:", m[key].nvals, "f:", front[key].nvals)
                m[key] += front[key]

        iter = 0

        # print_memory_use_in_kb("after m")
        # m_nvals = sum(v.nvals for v in m.values())
        # print("M:", m_nvals)
        # for (k, v) in m.items():
        #     print(k, ":", v.nvals, round(v.nvals / m_nvals * 100, 2), "%")

        last_percent = 0.0

        time_per_rule = defaultdict(lambda: 0.0)
        time_per_nont = defaultdict(lambda: 0.0)
        time_per_mask = defaultdict(lambda: 0.0)

        while True:
            # print("mem:", psutil.virtual_memory().percent)
            # if last_percent * 1.5 < psutil.virtual_memory().percent:
            #     print("collect")
            #     gc.collect()
            #     last_percent = psutil.virtual_memory().percent

            # if iter % 2 == 0:
            #     gc.collect()

            iter += 1
            print("Iter:", iter, "at", round(time() - t0, 3), "m.nvals", sum(v.nvals for v in m.values()))
            print("m.__sizeof__:", m.__sizeof__() / 1024, "f.__sizeof__:", front.__sizeof__() / 1024)
            print()

            new_front = DefaultKeyDependentDict(lambda var_name: (
                self.hyper_space.create_hyper_vector(DOMAIN, HyperVectorOrientation.VERTICAL)
                if var_name in self.hyper_grammar.hyper_nonterms
                else unique_ptr(Matrix(DOMAIN, self.graph.matrices_size, self.graph.matrices_size))
            ))

            if iter != 1:
                # print("M * F")
                for l, r1, r2 in self.hyper_grammar.complex_rules:
                        t0 = time()
                        if not OPTIMIZE_EMPTY or m[r1].nvals != 0 and front[r2].nvals != 0:
                            with SimpleTimer(f"{l} -> {r1} {r2}: ({m[r1].nvals}) x ({front[r2].nvals})"):
                                mxm = m[r1].mxm(front[r2], op=SEMIRING)
                            if mxm.nvals != 0:
                                mxm = self._fix_hyper_vector(mxm, reduce=l not in self.hyper_grammar.hyper_nonterms)
                                new_front[l] << new_front[l].ewise_add(mxm)
                                # mxm.__del__()
                        time_per_rule[(0, l, r1, r2)] += time() - t0
                for key in front:
                    with SimpleTimer(f"iadd {key}"):
                        t0 = time()
                        # print(f"iadd {key}")
                        m[key] += front[key]
                        time_per_nont[key] += time() - t0

            # print("F * M")
            for l, r1, r2 in self.hyper_grammar.complex_rules:
                t0 = time()
                if not OPTIMIZE_EMPTY or front[r1].nvals != 0 and m[r2].nvals != 0:
                    # m_cur = m[r2].to_matrix()
                    # f_cur = front[r1]
                    # for ff in [0, 1]:
                    #     for fm in [0, 1]:
                    #         f_cur.format = ff
                    #         m_cur.format = fm
                    #         with SimpleTimer(f"{l} -> {r1} {r2}: ({f_cur.nvals}, {ff}) x ({m_cur.nvals}, {fm})"):
                    #             mxm = f_cur.mxm(m_cur, semiring=SEMIRING)
                    with SimpleTimer(f"{l} -> {r1} {r2}: ({front[r1].nvals}) x ({m[r2].nvals})"):
                        mxm = m[r2].rmxm(front[r1], op=SEMIRING)
                    if mxm.nvals != 0:
                        mxm = self._fix_hyper_vector(mxm, reduce=l not in self.hyper_grammar.hyper_nonterms)
                        new_front[l] << new_front[l].ewise_add(mxm)
                        # mxm.__del__()
                time_per_rule[(1, l, r1, r2)] += time() - t0

            # for key in front:
            #     front[key].__del__()

            front = new_front
            # print("new_front.__sizeof__:", front.__sizeof__())
            for key in front:
                old = front[key]
                t0 = time()
                front[key] = m[key].r_complimentary_mask(front[key])
                time_per_mask[key] += time() - t0
                # if old is not front[key]:
                #     old.__del__()

            if all(v.nvals == 0 for v in front.values()):
                # print_memory_use_in_kb("after all")
                # m_nvals = sum(v.nvals for v in m.values())
                # print("M:", m_nvals)
                # for (k, v) in m.items():
                #     print(k, ":", v.nvals, round(v.nvals / m_nvals * 100, 2), "%")
                # print("size of enhanced:", m[self.hyper_grammar.start_nonterm].__sizeof__())
                matrix_S = m[self.hyper_grammar.start_nonterm].to_matrix()
                print("S size:", matrix_S.__sizeof__(), matrix_S.nvals, matrix_S.__sizeof__() / matrix_S.nvals)
                # print("Iters:", iter)
                t_all = time() - t_start
                # for k, v in sorted(time_per_nont.items(), key=lambda it: it[1]):
                #     print(k, "-\t", round(v / t_all * 100, 2), "%")
                # print()
                # for k, v in sorted(time_per_rule.items(), key=lambda it: it[1]):
                #     print(k, "-\t", round(v / t_all * 100, 2), "%")
                # print()
                # for k, v in sorted(time_per_mask.items(), key=lambda it: it[1]):
                #     print(k, "-\t", round(v / t_all * 100, 2), "%")
                return ResultAlgo(matrix_S, iter)

    def _create_front(self):
        front = DefaultKeyDependentDict(self._create_matrix_for_front)
        for l in self.hyper_grammar.eps_rules:
            front[l] = Vector.from_scalar(True, size=self.graph.matrices_size, dtype=DOMAIN).diag()
        for l, r in self.hyper_grammar.simple_rules:
            if r in self.graph.matrices:
                front[l] << front[l].ewise_add(
                    self.graph[r],
                    op=graphblas.monoid.any
                )
        for rule in self.hyper_grammar.hyper_simple_rules:
            front[rule.nonterm] << front[rule.nonterm].ewise_add(self.hyper_space.stack_into_hyper_column([
                # FIXME hack
                (
                    self.graph[label]
                    if label in self.graph.matrices
                    else unique_ptr(Matrix(DOMAIN, self.graph.matrices_size, self.graph.matrices_size))
                )
                for label in (
                    f"{rule.term_prefix}{str(i)}{rule.term_suffix}"
                    for i in range(self.hyper_grammar.hyper_nonterm_size)
                )
            ]),
                # FIXME bool specific code
                op=graphblas.monoid.any
            )
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
        # base_matrix.format = 0 if var_name in self.r2s_with_hyper_r1 or var_name in self.r2s_with_non_hyper_r1 else 1
        # return self.hyper_space.wrap_enhanced_hyper_matrix(MatrixToEnhancedAdapter(base_matrix))
        return self.hyper_space.wrap_enhanced_hyper_matrix(
            FormatOptimizedMatrix(
                # base_matrix is CSR, and we don't need to cache CSR if var_name never occurs in place of r2 in rules
                discard_base_on_reformat=(var_name not in self.r2s_with_hyper_r1 and var_name not in self.r2s_with_non_hyper_r1),
                # discard_base_on_reformat=False,
                base=
                IAddOptimizedMatrix(
                    MatrixToEnhancedAdapter(base_matrix)
                )
            )
        )

    def _create_matrix_for_front(self, var_name: str) -> Matrix:
        # if var_name in self.hyper_grammar.hyper_nonterms:
        #     matrix = self.hyper_space.create_hyper_vector(
        #         DOMAIN,
        #         HyperVectorOrientation.VERTICAL
        #         if var_name in self.r2s_with_hyper_r1 or var_name in self.r1s_with_non_hyper_r2
        #         else HyperVectorOrientation.HORIZONTAL
        #     )
        # else:
        #     matrix = Matrix.sparse(DOMAIN, self.graph.matrices_size, self.graph.matrices_size)
        # matrix.format = 0 if var_name in self.r2s_with_hyper_r1 or var_name in self.r2s_with_non_hyper_r1 else 1
        # return matrix
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
