from typing import Iterable
from abc import ABC, abstractmethod
from pyformlang.cfg import CFG
from src.graph.graph import Graph


class MultipleSourceProblem(ABC):
    """
    Base class for multiple-source problem
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
    def clear_src(self):
        pass

    @abstractmethod
    def solve(self, sources: Iterable):
        """
        Solve problem with graph and grammar
        """
        pass
