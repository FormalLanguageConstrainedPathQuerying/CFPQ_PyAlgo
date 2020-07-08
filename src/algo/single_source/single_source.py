from typing import Iterable
from pygraphblas import Matrix

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph


class SingleSourceIndex:
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        self.graph = graph
        self.grammar = grammar
        self.sources = LabelGraph()
        self.nonterms = LabelGraph()

    def init_simple_rules(self):
        for l, r in self.grammar.simple_rules:
            self.sources[l] = self.graph[r].dup()


class SingleSourceAlgo:
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        self.graph = graph
        self.grammar = grammar
        self.index = SingleSourceIndex(graph, grammar)

    def solve(self, sources_vertices: Iterable) -> Matrix:
        pass
