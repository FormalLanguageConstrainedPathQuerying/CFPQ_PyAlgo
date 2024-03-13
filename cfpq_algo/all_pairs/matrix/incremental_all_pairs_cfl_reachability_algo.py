from typing import List

from cfpq_algo.all_pairs.all_pairs_cfl_reachability_algo import (
    AllPairsCflReachabilityAlgoInstance,
    AllPairsCflReachabilityAlgo
)
from cfpq_algo.all_pairs.matrix.abstract_all_pairs_cfl_reachability import \
    AbstractAllPairsCflReachabilityMatrixAlgoInstance
from cfpq_algo.setting.algo_setting import AlgoSetting
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph


class IncrementalAllPairsCFLReachabilityMatrixAlgoInstance(
    AbstractAllPairsCflReachabilityMatrixAlgoInstance
):
    def compute_transitive_closure(self):
        front = self.graph.to_unoptimized()
        self.graph = self.graph.empty_copy()
        while front.nvals != 0:
            new_front = self.graph.mxm(front, self.grammar, op=self.semiring)
            self.graph.iadd(front, op=self.monoid)
            self.graph.rmxm(
                front,
                self.grammar,
                accum=new_front,
                op=self.semiring
            )
            for (lhs, rhs) in self.grammar.simple_rules:
                if rhs in self.grammar.non_terminals:
                    new_front.iadd_by_symbol(lhs, front[rhs], op=self.monoid)
            front = new_front.to_unoptimized()
            front = self.graph.rsub(front, op=self.algebraic_structure.sub_op)


class IncrementalAllPairsCFLReachabilityMatrixAlgo(AllPairsCflReachabilityAlgo):
    def _create_instance(self, graph: LabelDecomposedGraph, grammar: CnfGrammarTemplate,
                         settings: List[AlgoSetting]) -> AllPairsCflReachabilityAlgoInstance:
        return IncrementalAllPairsCFLReachabilityMatrixAlgoInstance(graph, grammar, settings)

    @property
    def name(self) -> str:
        return "IncrementalAllPairsCFLReachabilityMatrix"
