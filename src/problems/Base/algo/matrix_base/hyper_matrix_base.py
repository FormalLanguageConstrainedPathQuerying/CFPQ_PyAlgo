from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector
from pyformlang.cfg import CFG

from graphblas.core.dtypes import BOOL
from graphblas.semiring import any_pair
import graphblas.monoid

from src.grammar.hyper_cnf_grammar import HyperCnfGrammar
from src.graph.graph import Graph
from src.matrix.enhanced_matrix import EnhancedMatrix
from src.matrix.hyper_matrix_space import HyperMatrixSpace, HyperVectorOrientation
from src.matrix.hyper_square_matrix_space import HyperSquareMatrixSpace
from src.matrix.matrix_to_enhanced_adapter import MatrixToEnhancedAdapter

from src.problems.Base.Base import BaseProblem

from src.grammar.cnf_grammar import CnfGrammar
from src.problems.utils import ResultAlgo
from src.utils.default_dict import DefaultKeyDependentDict


DOMAIN = BOOL
SEMIRING = any_pair
MONOID = graphblas.monoid.any


class HyperMatrixBaseAlgo(BaseProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_python_graphblas_bool_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)
        self.hyper_grammar = HyperCnfGrammar.from_cnf(self.grammar)

    def inject_cnf_grammar(self, grammar: CnfGrammar):
        self.grammar = grammar
        self.hyper_grammar = HyperCnfGrammar.from_cnf(self.grammar)

    def inject_hyper_cnf_grammar(self, grammar: HyperCnfGrammar):
        self.hyper_grammar = grammar

    def solve(self):
        self.hyper_nonterm_size = self.hyper_grammar.get_hyper_nonterm_size(self.graph.matrices.keys())

        self.hyper_space: HyperMatrixSpace = HyperSquareMatrixSpace(
            n=self.graph.matrices_size,
            hyper_size=self.hyper_nonterm_size
        )

        self._analyze_complex_rules()

        m = DefaultKeyDependentDict(self._create_enhanced_matrix_for_var)

        for l in self.hyper_grammar.eps_rules:
            m[l] += Vector.from_scalar(True, size=self.graph.matrices_size, dtype=DOMAIN).diag()
        for l, r in self.hyper_grammar.simple_rules:
            m[l] += self.graph[r]
        for rule in self.hyper_grammar.hyper_simple_rules:
            m[rule.nonterm] += self.hyper_space.stack_into_hyper_column([
                self.graph[label]
                for label in (
                    f"{rule.term_prefix}{str(i)}{rule.term_suffix}"
                    for i in range(self.hyper_nonterm_size)
                )
            ])

        changed = True
        iter = 0
        while changed:
            iter += 1
            changed = False
            for l, r1, r2 in self.hyper_grammar.complex_rules:
                old_nnz = m[l].nvals
                mxm = m[r1].mxm(m[r2].to_matrix(), op=SEMIRING)
                m[l] += (
                    mxm if l in self.hyper_grammar.hyper_nonterms else self.hyper_space.reduce_hyper_vector_or_cell(mxm)
                )
                new_nnz = m[l].nvals
                changed |= not old_nnz == new_nnz
        return ResultAlgo(m[self.hyper_grammar.start_nonterm].to_matrix(), iter)

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
            base_matrix = Matrix(DOMAIN, self.graph.matrices_size, self.graph.matrices_size)

        return self.hyper_space.wrap_enhanced_hyper_matrix(
            MatrixToEnhancedAdapter(base_matrix)
        )

    def prepare_for_solve(self):
        pass
