from abc import ABC, abstractmethod
from pathlib import Path


class AllPathsProblem(ABC):
    """
    Base class for all paths problem
    """

    @abstractmethod
    def prepare(self, graph: Path, grammar: Path):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        pass
