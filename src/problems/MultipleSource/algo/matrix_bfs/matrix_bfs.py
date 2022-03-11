from pyformlang.cfg import CFG

from src.grammar.rsa import RecursiveAutomaton

from src.graph.graph import Graph
from src.graph.label_graph import LabelGraph

from src.problems.AllPaths.AllPaths import AllPathsProblem
from src.problems.utils import ResultAlgo


class ProblemAlgo(AllPathsProblem):
    """
    For now we have regular grammar only in this algo.
    Hence this is to be implemented with CFG.
    """

    def prepare(self, graph: Graph, grammar: CFG):
        pass

    def prepare_for_solve(self):
        pass

    def solve(self):
        pass

    def prepare_for_exctract_paths(self):
        pass

    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        pass
