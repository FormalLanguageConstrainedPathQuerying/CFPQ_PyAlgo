from abc import ABC, abstractmethod
from pyformlang.cfg import CFG
from src.graph.graph import Graph


class BaseProblem(ABC):
    """
    Base class for base problem
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
