from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser
from typing import List

from cfpq_algo.setting.algo_setting import AlgoSetting
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph
from cfpq_model.utils import explode_indices


class PreProcessorSetting(AlgoSetting, ABC):
    @abstractmethod
    def preprocess(
        self,
        graph: LabelDecomposedGraph,
        grammar: CnfGrammarTemplate
    ) -> (LabelDecomposedGraph, CnfGrammarTemplate):
        pass


def preprocess_graph_and_grammar(
    graph: LabelDecomposedGraph,
    grammar: CnfGrammarTemplate,
    algo_settings: List[AlgoSetting]
):
    for algo_setting in algo_settings:
        if isinstance(algo_setting, PreProcessorSetting):
            algo_setting.was_used_by_algo = True
            graph, grammar = algo_setting.preprocess(graph, grammar)
    return graph, grammar


class IndexExplodingPreProcessorSetting(PreProcessorSetting):
    def __init__(self):
        super().__init__()
        self.is_enabled = False

    def __repr__(self):
        return f"{self.__class__.__name__}(is_enabled={self.is_enabled})"

    @property
    def flag_name(self) -> str:
        return "--disable-optimize-block-matrix"

    @property
    def var_name(self) -> str:
        return "explode_indexes"

    def add_arg(self, parser: ArgumentParser):
        parser.add_argument(
            self.flag_name,
            dest=self.var_name,
            default=False,
            action="store_true",
            help="Turns off block matrix optimization."
        )

    def read_arg(self, args: Namespace):
        if args.explode_indexes:
            self.was_specified_by_user = True
            self.is_enabled = True

    def preprocess(
        self,
        graph: LabelDecomposedGraph,
        grammar: CnfGrammarTemplate
    ) -> (LabelDecomposedGraph, CnfGrammarTemplate):
        if not self.is_enabled:
            return graph, grammar

        return explode_indices(graph, grammar)
