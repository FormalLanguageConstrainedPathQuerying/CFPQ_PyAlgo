from abc import ABC, abstractmethod
from pyformlang.cfg import CFG
from src.graph.graph import Graph


class AllPathsProblem(ABC):
    """
    Base class for all paths problem
    """

    @abstractmethod
    def prepare(self, graph: Graph, grammar: CFG):
        """
        Prepare for the operation of the algorithm: load graph and grammar
        @param graph: path to file with graph
        @param grammar: path to file with grammar
        """
        pass

    @abstractmethod
    def solve(self):
        """
        Solve problem with graph and grammar
        """
        pass

    @abstractmethod
    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        """
        Extract all paths between two vertices, the length of which does not exceed the given parameter
        @param v_start: starting vertex for paths
        @param v_finish: finishing vertex for paths
        @param nonterminal: nonterminal from which paths are being restored
        @param max_len: path length limitation
        """
        pass
