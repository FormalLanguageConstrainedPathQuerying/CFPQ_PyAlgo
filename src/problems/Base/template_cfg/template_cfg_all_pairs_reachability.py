from abc import ABC, abstractmethod
from typing import List

from graphblas.core.matrix import Matrix

from src.algo_setting.algo_setting import AlgoSetting
from src.grammar.cnf_grammar_template import CnfGrammarTemplate
from src.graph.label_decomposed_graph import LabelDecomposedGraph


class AllPairsCflReachabilityAlgoInstance(ABC):
    @abstractmethod
    def solve(self) -> Matrix:
        pass


class AllPairsCflReachabilityAlgo(ABC):
    def solve(
            self,
            graph: LabelDecomposedGraph,
            grammar: CnfGrammarTemplate,
            settings: List[AlgoSetting]
    ) -> Matrix:
        return self._create_instance(graph, grammar, settings).solve()

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _create_instance(
            self,
            graph: LabelDecomposedGraph,
            grammar: CnfGrammarTemplate,
            settings: List[AlgoSetting]
    ) -> AllPairsCflReachabilityAlgoInstance:
        """
        Creates algo instance that solves all-pairs CFL-r problem for given graph and grammar.

        Algo instance encapsulates intermediate solving state between algorithm steps.
        """
        pass
