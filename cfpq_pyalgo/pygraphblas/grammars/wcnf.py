from typing import List

from pyformlang.cfg import CFG, Variable, Terminal, Epsilon, Production

__all__ = [
    "WCNF",
]


class WCNF:
    def __init__(self, cfg: CFG):
        self._cfg: CFG = cfg
        self._cnf: CFG = cfg.to_normal_form()
        self.start_symbol: Variable = cfg.start_symbol

        self.epsilon_productions: List[Production] = []
        self.unary_productions: List[Production] = []
        self.binary_productions: List[Production] = []

        for production in self._cfg.productions:
            if production.body in ([], Epsilon):
                self.epsilon_productions.append(production)

        for production in self._cnf.productions:
            if len(production.body) == 1:
                self.unary_productions.append(production)
            elif len(production.body) == 2:
                self.binary_productions.append(production)

        self.productions = (
                self.epsilon_productions
                + self.unary_productions
                + self.binary_productions
        )

        self.variables = []
        self.terminals = []

        for production in self.productions:
            self.variables.append(production.head)

            for term in production.body:
                if isinstance(term, Terminal):
                    self.terminals.append(term)
                elif isinstance(term, Variable):
                    self.variables.append(term)

    def contains(self, word: str):
        return self._cfg.contains(word)
