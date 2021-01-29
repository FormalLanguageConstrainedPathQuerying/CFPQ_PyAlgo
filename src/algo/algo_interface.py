from abc import ABC, abstractmethod
from pathlib import Path


class CFPQAlgo(ABC):
    @abstractmethod
    def __init__(self, path_to_graph: Path, path_to_grammar: Path):
        self.graph = None
        self.grammar = None
        pass

    @abstractmethod
    def solve(self):
        pass
