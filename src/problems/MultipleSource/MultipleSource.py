from typing import Iterable
from abc import ABC, abstractmethod
from pathlib import Path


class MultipleSourceProblem(ABC):
    """
    Base class for multiple-source problem
    """

    @abstractmethod
    def prepare(self, graph: Path, grammar: Path):
        pass

    @abstractmethod
    def solve(self, sources: Iterable):
        pass
