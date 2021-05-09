from abc import ABC, abstractmethod
from pathlib import Path


class BaseProblem(ABC):
    """
    Base class for base problem
    """

    @abstractmethod
    def prepare(self, graph: Path, grammar: Path):
        pass

    @abstractmethod
    def solve(self):
        pass
