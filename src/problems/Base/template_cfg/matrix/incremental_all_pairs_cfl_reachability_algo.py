from typing import List

from src.algo_setting.algo_setting import AlgoSetting
from src.grammar.cnf_grammar_template import CnfGrammarTemplate
from src.graph.label_decomposed_graph import OptimizedLabelDecomposedGraph, LabelDecomposedGraph
from src.problems.Base.template_cfg.matrix.abstract_all_pairs_cfl_reachability import \
    AbstractAllPairsCflReachabilityMatrixAlgoInstance
from src.problems.Base.template_cfg.template_cfg_all_pairs_reachability import AllPairsCflReachabilityAlgoInstance, \
    AllPairsCflReachabilityAlgo


class IncrementalAllPairsCFLReachabilityMatrixAlgoInstance(AbstractAllPairsCflReachabilityMatrixAlgoInstance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compute_transitive_closure(self):
        front = self.graph.to_unoptimized()
        self.graph = self.graph.empty_copy()
        while front.nvals != 0:
            new_front = self.graph.mxm(front, self.grammar, op=self.algebraic_structure.semiring)
            self.graph += front
            self.graph.rmxm(
                front,
                self.grammar,
                accum=new_front,
                op=self.algebraic_structure.semiring
            )
            front = new_front.to_unoptimized()
            front = self.graph.r_complimentary_mask(front)


class IncrementalAllPairsCFLReachabilityMatrixAlgo(AllPairsCflReachabilityAlgo):
    def _create_instance(self, graph: LabelDecomposedGraph, grammar: CnfGrammarTemplate,
                         settings: List[AlgoSetting]) -> AllPairsCflReachabilityAlgoInstance:
        return IncrementalAllPairsCFLReachabilityMatrixAlgoInstance(graph, grammar, settings)

    @property
    def name(self) -> str:
        return "IncrementalAllPairsCFLReachabilityMatrix"
