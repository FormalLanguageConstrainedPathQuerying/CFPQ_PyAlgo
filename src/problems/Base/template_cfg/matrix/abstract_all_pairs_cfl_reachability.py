from abc import ABC, abstractmethod
from typing import List

from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector
from graphblas.semiring import any_pair

from src.algo_setting.algo_setting import AlgoSetting
from src.grammar.cnf_grammar_template import CnfGrammarTemplate
from src.graph.label_decomposed_graph import OptimizedLabelDecomposedGraph, LabelDecomposedGraph
from src.matrix.matrix_optimizer_setting import get_matrix_optimizer_settings
from src.matrix.utils import complimentary_mask
from src.problems.Base.template_cfg.template_cfg_all_pairs_reachability import AllPairsCflReachabilityAlgoInstance
from src.utils.typed_subtractable_semiring import SubtractableSemiring


class AbstractAllPairsCflReachabilityMatrixAlgoInstance(AllPairsCflReachabilityAlgoInstance, ABC):
    def __init__(
        self,
        graph: LabelDecomposedGraph,
        grammar: CnfGrammarTemplate,
        settings: List[AlgoSetting],
        algebraic_structure: SubtractableSemiring = SubtractableSemiring(
            one=True,
            semiring=any_pair,
            sub_op=lambda minuend, subtrahend: complimentary_mask(minuend, subtrahend, any_pair)
        )
    ):
        matrix_optimizers = get_matrix_optimizer_settings(settings)
        AlgoSetting.mark_as_used_by_algo(matrix_optimizers)
        self.graph = OptimizedLabelDecomposedGraph.from_unoptimized(graph, matrix_optimizers)
        self.grammar = grammar
        self.settings = settings
        self.algebraic_structure = algebraic_structure

    def solve(self) -> Matrix:
        self.add_epsilon_edges()
        self.add_edges_for_simple_rules()
        self.compute_transitive_closure()
        return self.graph[self.grammar.start_nonterm]

    @abstractmethod
    def compute_transitive_closure(self):
        pass

    def add_epsilon_edges(self):
        if len(self.grammar.epsilon_rules) == 0:
            return
        identity_matrix = Vector.from_scalar(
            self.algebraic_structure.one,
            size=self.graph.vertex_count,
            dtype=self.graph.dtype
        ).diag()
        for non_terminal in self.grammar.epsilon_rules:
            self.graph.iadd_by_symbol(non_terminal, identity_matrix)

    def add_edges_for_simple_rules(self):
        for (non_terminal, terminal) in self.grammar.simple_rules:
            self.graph.iadd_by_symbol(non_terminal, self.graph[terminal])
