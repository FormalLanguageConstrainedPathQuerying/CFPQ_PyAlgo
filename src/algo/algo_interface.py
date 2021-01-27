from abc import ABC, abstractmethod


class CFPQAlgo(ABC):
    @abstractmethod
    def __init__(self, path_to_graph: str, path_to_grammar: str):
        self.graph = None
        self.grammar = None
        pass

    @abstractmethod
    def solve(self):
        pass
