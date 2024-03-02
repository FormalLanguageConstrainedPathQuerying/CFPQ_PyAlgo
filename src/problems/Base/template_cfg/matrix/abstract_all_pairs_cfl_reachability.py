from abc import ABC, abstractmethod
from typing import List

from graphblas.core.matrix import Matrix
from graphblas.core.operator import Semiring, Monoid
from graphblas.semiring import any_pair

from src.algo_setting.algo_setting import AlgoSetting
from src.grammar.cnf_grammar_template import CnfGrammarTemplate
from src.graph.label_decomposed_graph import OptimizedLabelDecomposedGraph, LabelDecomposedGraph
from src.matrix.matrix_optimizer_setting import get_matrix_optimizer_settings
from src.matrix.utils import complimentary_mask, identity_matrix
from src.problems.Base.template_cfg.template_cfg_all_pairs_reachability import AllPairsCflReachabilityAlgoInstance
from src.utils.subtractable_semiring import SubtractableSemiring


class AbstractAllPairsCflReachabilityMatrixAlgoInstance(AllPairsCflReachabilityAlgoInstance, ABC):
    def __init__(
        self,
        graph: LabelDecomposedGraph,
        grammar: CnfGrammarTemplate,
        settings: List[AlgoSetting],
        algebraic_structure: SubtractableSemiring = SubtractableSemiring(
            one=True,
            semiring=any_pair,
            sub_op=lambda minuend, subtrahend: complimentary_mask(minuend, subtrahend)
        )
    ):
        matrix_optimizers = get_matrix_optimizer_settings(settings)
        self.graph = OptimizedLabelDecomposedGraph.from_unoptimized(graph, matrix_optimizers)
        self.grammar = grammar
        self.settings = settings
        self.algebraic_structure = algebraic_structure

    @property
    def semiring(self) -> Semiring:
        return self.algebraic_structure.semiring

    @property
    def monoid(self) -> Monoid:
        return self.semiring.monoid

    def solve(self) -> Matrix:
        self.add_epsilon_edges()
        self.add_edges_for_simple_terminal_rules()
        self.compute_transitive_closure()
        return self.graph[self.grammar.start_nonterm]

    @abstractmethod
    def compute_transitive_closure(self):
        pass

    def add_epsilon_edges(self):
        if len(self.grammar.epsilon_rules) == 0:
            return
        id_matrix = identity_matrix(
            one=self.algebraic_structure.one,
            size=self.graph.vertex_count,
            dtype=self.graph.dtype
        )
        for non_terminal in self.grammar.epsilon_rules:
            self.graph.iadd_by_symbol(non_terminal, id_matrix, op=self.monoid)

    def add_edges_for_simple_terminal_rules(self):
        for (lhs, rhs) in self.grammar.simple_rules:
            self.graph.iadd_by_symbol(lhs, self.graph[rhs], op=self.monoid)
