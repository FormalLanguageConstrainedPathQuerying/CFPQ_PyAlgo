from typing import List

from cfpq_algo.all_pairs.all_pairs_cfl_reachability_algo import (
    AllPairsCflReachabilityAlgoInstance,
    AllPairsCflReachabilityAlgo
)
from cfpq_algo.all_pairs.matrix.abstract_all_pairs_cfl_reachability import \
    AbstractAllPairsCflReachabilityMatrixAlgoInstance
from cfpq_algo.setting.algo_setting import AlgoSetting
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate
from cfpq_model.label_decomposed_graph import OptimizedLabelDecomposedGraph, LabelDecomposedGraph


class NonIncrementalAllPairsCFLReachabilityMatrixAlgoInstance(
    AbstractAllPairsCflReachabilityMatrixAlgoInstance
):
    def compute_transitive_closure(self) -> OptimizedLabelDecomposedGraph:
        old_nvals = self.graph.nvals
        while True:
            for (lhs, rhs) in self.grammar.simple_rules:
                if rhs in self.grammar.non_terminals:
                    self.graph.iadd_by_symbol(lhs, self.graph[rhs], op=self.monoid)
            self.graph.mxm(
                self.graph.to_unoptimized(),
                self.grammar,
                accum=self.graph,
                op=self.semiring
            )
            new_nvals = self.graph.nvals
            if old_nvals == new_nvals:
                return self.graph
            old_nvals = new_nvals


class NonIncrementalAllPairsCFLReachabilityMatrixAlgo(AllPairsCflReachabilityAlgo):
    def _create_instance(self, graph: LabelDecomposedGraph, grammar: CnfGrammarTemplate,
                         settings: List[AlgoSetting]) -> AllPairsCflReachabilityAlgoInstance:
        return NonIncrementalAllPairsCFLReachabilityMatrixAlgoInstance(graph, grammar, settings)

    @property
    def name(self) -> str:
        return "NonIncrementalAllPairsCFLReachabilityMatrix"
