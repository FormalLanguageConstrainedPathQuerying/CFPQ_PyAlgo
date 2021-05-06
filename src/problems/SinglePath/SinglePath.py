from abc import ABC, abstractmethod
from pathlib import Path


class SinglePathProblem(ABC):
    """
    Base class for single path problem
    """

    @abstractmethod
    def prepare(self, graph: Path, grammar: Path):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def getPath(self, v_start: int, v_finish: int, nonterminal: str):
        pass
