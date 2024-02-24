from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser
from typing import List

from src.algo_setting.algo_setting import AlgoSetting
from src.grammar.cnf_grammar_template import CnfGrammarTemplate, Symbol
from src.graph.label_decomposed_graph import LabelDecomposedGraph


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
        return "-" + self.var_name.replace('_', '-')

    @property
    def var_name(self) -> str:
        return "explode_indexes"

    def add_arg(self, parser: ArgumentParser):
        parser.add_argument(self.flag_name, dest=self.var_name, default=False, action="store_true")

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

        block_matrix_space = graph.block_matrix_space
        block_count = block_matrix_space.block_count

        matrices = dict()
        for symbol, matrix in graph.matrices.items():
            if block_matrix_space.is_single_cell(matrix.shape):
                matrices[symbol] = matrix
            else:
                for i, block in enumerate(block_matrix_space.get_hyper_vector_blocks(matrix)):
                    matrices[_index_symbol(symbol, i)] = block

        epsilon_rules = []
        for non_terminal in grammar.epsilon_rules:
            if non_terminal.is_indexed:
                for i in range(block_count):
                    epsilon_rules.append(_index_symbol(non_terminal, i))
            else:
                epsilon_rules.append(non_terminal)

        simple_rules = []
        for (non_terminal, terminal) in grammar.simple_rules:
            if non_terminal.is_indexed or terminal.is_indexed:
                for i in range(block_count):
                    simple_rules.append((_index_symbol(non_terminal, i), _index_symbol(terminal, i)))
            else:
                simple_rules.append((non_terminal, terminal))

        complex_rules = []
        for (non_terminal, symbol1, symbol2) in grammar.complex_rules:
            if non_terminal.is_indexed or symbol1.is_indexed or symbol2.is_indexed:
                for i in range(block_count):
                    complex_rules.append((
                        _index_symbol(non_terminal, i),
                        _index_symbol(symbol1, i),
                        _index_symbol(symbol2, i),
                    ))
            else:
                complex_rules.append((non_terminal, symbol1, symbol2))

        return (
            LabelDecomposedGraph(
                vertex_count=graph.vertex_count,
                block_matrix_space=block_matrix_space,
                dtype=graph.dtype,
                matrices=matrices
            ),
            CnfGrammarTemplate(
                start_nonterm=grammar.start_nonterm,
                epsilon_rules=epsilon_rules,
                simple_rules=simple_rules,
                complex_rules=complex_rules
            )
        )


def _index_symbol(symbol: Symbol, index: int) -> Symbol:
    return Symbol(f"{symbol.label}_{index}") if symbol.is_indexed else symbol
