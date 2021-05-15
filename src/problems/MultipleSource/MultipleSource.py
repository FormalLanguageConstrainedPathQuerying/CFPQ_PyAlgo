from typing import Iterable
from abc import ABC, abstractmethod
from pathlib import Path


class MultipleSourceProblem(ABC):
    """
    Base class for multiple-source problem
    """

    @abstractmethod
    def prepare(self, graph: Path, grammar: Path):
        """
        Prepare for the operation of the algorithm: load graph and grammar
        @param graph: path to file with graph
        @param grammar: path to file with grammar
        """
        pass

    @abstractmethod
    def solve(self, sources: Iterable):
        """
        Solve problem with graph and grammar
        """
        pass
