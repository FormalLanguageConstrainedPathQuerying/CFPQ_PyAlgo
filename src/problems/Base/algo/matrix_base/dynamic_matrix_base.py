from typing import Optional

from line_profiler import LineProfiler
from pyformlang.cfg import CFG
from pygraphblas import BOOL, Matrix

from src.grammar.cnf_grammar import CnfGrammar
from src.grammar.hyper_cnf_grammar import HyperCnfGrammar
from src.grammar.java_points_to_analysis import create_java_points_to_hyper_grammar
from src.graph.graph import Graph
from src.matrix.enhanced_matrix import OPTIMIZE_EMPTY, EnhancedMatrix
from src.matrix.hyper_matrix_space import HyperVectorOrientation, HyperMatrixSpace
from src.matrix.hyper_matrix_utils import HyperMatrixUtils
from src.matrix.iadd_optimized_matrix import IAddOptimizedMatrix
from src.matrix.format_optimized_matrix import FormatOptimizedMatrix
from src.matrix.matrix_to_enhanced_adapter import MatrixToEnhancedAdapter
from src.matrix.hyper_square_matrix_space import HyperSquareMatrixSpace
from src.problems.Base.Base import BaseProblem
from src.problems.utils import ResultAlgo
from src.utils.default_dict import DefaultKeyDependentDict

DOMAIN = BOOL
SEMIRING = DOMAIN.ANY_PAIR


class DynamicMatrixBaseAlgo(BaseProblem):
    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_bool_graph()
        # TODO weak cnf?
        self.grammar = CnfGrammar.from_cfg(grammar)
        self.profiler: Optional[LineProfiler] = None

    def inject_cnf_grammar(self, grammar: CnfGrammar):
        self.grammar = grammar

    def inject_profiler(self, profiler):
        self.profiler = profiler

    def solve(self):
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
            self.profiler.add_function(self._fix_hyper_vector)
            self.profiler.add_function(HyperMatrixUtils.hyper_row_to_hyper_column)
            self.profiler.add_function(HyperMatrixUtils.hyper_column_to_hyper_row)
            self.profiler.add_function(HyperMatrixUtils.hyper_column_to_hyper_matrix)
            self.profiler.add_function(HyperMatrixUtils.reduce_hyper_row)
            self.profiler.add_function(HyperMatrixUtils.reduce_hyper_column)

        # if self.profiler is not None:
        #     self.profiler.add_function(fix_hyper_vector)
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
        # memorized = []

        while True:
            iter += 1
            new_front = DefaultKeyDependentDict(lambda var_name: (
                self.hyper_space.create_hyper_vector(DOMAIN, HyperVectorOrientation.VERTICAL)
                if var_name in self.hyper_grammar.hyper_nonterms
                else Matrix.sparse(DOMAIN, self.graph.matrices_size, self.graph.matrices_size)
            ))

            if iter != 1:
                # print("M * F")
                for l, r1, r2 in self.hyper_grammar.complex_rules:
                        if not OPTIMIZE_EMPTY or m[r1].nvals != 0 and front[r2].nvals != 0:
                            # with SimpleTimer(f"{l} -> {r1} {r2}: ({m[r1].nvals}, {m[r1].format}) x ({front[r2].nvals}, {front[r2].format})"):
                            mxm = m[r1].mxm(front[r2], semiring=SEMIRING)
                            if mxm.nvals != 0:
                                mxm = self._fix_hyper_vector(mxm, reduce=l not in self.hyper_grammar.hyper_nonterms)
                                new_front[l] += mxm
                for key in front:
                    m[key] += front[key]

            # print("F * M")
            for l, r1, r2 in self.hyper_grammar.complex_rules:
                if not OPTIMIZE_EMPTY or front[r1].nvals != 0 and m[r2].nvals != 0:
                    # m_cur = m[r2].to_matrix()
                    # f_cur = front[r1]
                    # for ff in [0, 1]:
                    #     for fm in [0, 1]:
                    #         f_cur.format = ff
                    #         m_cur.format = fm
                    #         with SimpleTimer(f"{l} -> {r1} {r2}: ({f_cur.nvals}, {ff}) x ({m_cur.nvals}, {fm})"):
                    #             mxm = f_cur.mxm(m_cur, semiring=SEMIRING)
                    # with SimpleTimer(f"{l} -> {r1} {r2}: ({front[r1].nvals}, {front[r1].format}) x ({m[r2].nvals}, {m[r2].format})"):
                    mxm = m[r2].rmxm(front[r1], semiring=SEMIRING)
                    if mxm.nvals != 0:
                        mxm = self._fix_hyper_vector(mxm, reduce=l not in self.hyper_grammar.hyper_nonterms)
                        new_front[l] += mxm

            front = new_front
            for key in front:
                # memorized.append(front[key])
                front[key] = m[key].r_complimentary_mask(front[key])

            if all(v.nvals == 0 for v in front.values()):
                m_nvals = sum(v.nvals for v in m.values())
                print("M:", m_nvals)
                for (k, v) in m.items():
                    print(k, ":", v.nvals, round(v.nvals / m_nvals * 100, 2), "%")
                return ResultAlgo(m[self.hyper_grammar.start_nonterm].to_matrix(), iter)

    def _create_front(self):
        front = DefaultKeyDependentDict(self._create_matrix_for_front)
        identity = None
        for l in self.hyper_grammar.eps_rules:
            if identity is None:
                identity = Matrix.identity(DOMAIN, self.graph.matrices_size)
                front[l] = identity
            else:
                front[l] = identity.dup()
        for l, r in self.hyper_grammar.simple_rules:
            front[l] += self.graph[r]
        for rule in self.hyper_grammar.hyper_simple_rules:
            front[rule.nonterm] += self.hyper_space.stack_into_hyper_column([
                self.graph[f"{rule.term_prefix}{str(i)}{rule.term_suffix}"]
                for i in range(self.hyper_grammar.hyper_nonterm_size)
            ])
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
            base_matrix = Matrix.sparse(DOMAIN, self.graph.matrices_size, self.graph.matrices_size)
        # base_matrix.format = 0 if var_name in self.r2s_with_hyper_r1 or var_name in self.r2s_with_non_hyper_r1 else 1
        # return self.hyper_space.wrap_enhanced_hyper_matrix(MatrixToEnhancedAdapter(base_matrix))
        return self.hyper_space.wrap_enhanced_hyper_matrix(
            FormatOptimizedMatrix(
                # base_matrix is CSR, and we don't need to cache CSR if var_name never occurs in place of r2 in rules
                discard_base_on_reformat=(var_name not in self.r2s_with_hyper_r1 and var_name not in self.r2s_with_non_hyper_r1),
                # discard_base_on_reformat=False,
                base=IAddOptimizedMatrix(
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
            else Matrix.sparse(DOMAIN, self.graph.matrices_size, self.graph.matrices_size)
        )

    def _fix_hyper_vector(self, hyper_vector: Matrix, reduce: bool) -> Matrix:
        return self.hyper_space.reduce_hyper_vector_or_cell(hyper_vector) if reduce else self.hyper_space.hyper_rotate(
            hyper_vector, HyperVectorOrientation.VERTICAL)

    def prepare_for_solve(self):
        pass
