from typing import List

from src.algo_setting.algo_setting import AlgoSetting
from src.grammar.cnf_grammar_template import CnfGrammarTemplate
from src.graph.label_decomposed_graph import OptimizedLabelDecomposedGraph, LabelDecomposedGraph
from src.problems.Base.template_cfg.matrix.abstract_all_pairs_cfl_reachability import \
    AbstractAllPairsCflReachabilityMatrixAlgoInstance
from src.problems.Base.template_cfg.template_cfg_all_pairs_reachability import AllPairsCflReachabilityAlgoInstance, \
    AllPairsCflReachabilityAlgo


class NonIncrementalAllPairsCFLReachabilityMatrixAlgoInstance(AbstractAllPairsCflReachabilityMatrixAlgoInstance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compute_transitive_closure(self) -> OptimizedLabelDecomposedGraph:
        old_nvals = self.graph.nvals
        while True:
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
