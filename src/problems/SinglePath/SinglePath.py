from abc import ABC, abstractmethod
from pyformlang.cfg import CFG
from src.graph.graph import Graph


class SinglePathProblem(ABC):
    """
    Base class for single path problem
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
    def getPath(self, v_start: int, v_finish: int, nonterminal: str):
        """
        Extract one path between two vertices
        @param v_start: starting vertex for path
        @param v_finish: finishing vertex for path
        @param nonterminal: nonterminal from which path are being restored
        """
        pass
