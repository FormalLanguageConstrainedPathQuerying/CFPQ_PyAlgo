"""Base class for Weak Chomsky Normal Form"""
from typing import List

from pyformlang.cfg import CFG, Variable, Terminal, Epsilon, Production

__all__ = [
    "WCNF",
]


class WCNF:
    """A Context-Free Grammar class in which products take the following form:
    - A -> B C
    - A -> a
    - A -> epsilon
    where `A`, `B` and `C` are variables; `a` is an arbitrary terminal

    Also known as Weak Chomsky Normal Form

    Parameters
    ----------
    cfg: CFG
        Context-Free Grammar
    """

    def __init__(self, cfg: CFG):
        self._cfg: CFG = cfg
        self.start_variable: Variable = cfg.start_symbol

        if not _is_in_wcnf(cfg):
            cnf = cfg.to_normal_form()
        else:
            cnf = cfg

        self.epsilon_productions: List[Production] = []
        self.unary_productions: List[Production] = []
        self.binary_productions: List[Production] = []

        for production in self._cfg.productions:
            if production.body in ([], Epsilon):
                if production not in self.epsilon_productions:
                    self.epsilon_productions.append(production)

        for production in cnf.productions:
            if len(production.body) == 1:
                if production not in self.unary_productions:
                    self.unary_productions.append(production)
            elif len(production.body) == 2:
                if production not in self.binary_productions:
                    self.binary_productions.append(production)

        self.productions = (
            self.epsilon_productions + self.unary_productions + self.binary_productions
        )

        self.variables: List[Variable] = []
        self.terminals: List[Terminal] = []

        for production in self.productions:
            if production.head not in self.variables:
                self.variables.append(production.head)

            for term in production.body:
                if isinstance(term, Terminal):
                    if term not in self.terminals:
                        self.terminals.append(term)
                elif isinstance(term, Variable):
                    if term not in self.variables:
                        self.variables.append(term)

        self.variables.sort(key=str)
        self.terminals.sort(key=str)
        self.epsilon_productions.sort(key=str)
        self.unary_productions.sort(key=str)
        self.unary_productions.sort(key=str)
        self.binary_productions.sort(key=str)
        self.productions.sort(key=str)

    def contains(self, word: str):
        return self._cfg.contains(word)

    @classmethod
    def from_text(cls, text: str, start_variable: Variable = Variable("S")):
        cfg = CFG.from_text(text, start_variable)
        return cls(cfg)


def _is_in_wcnf(cfg: CFG) -> bool:
    for production in cfg.productions:
        if len(production.body) > 2:
            return False
        elif len(production.body) == 2:
            if not (
                isinstance(production.body[0], Variable)
                and isinstance(production.body[1], Variable)
            ):
                return False
        elif len(production.body) == 1:
            if not isinstance(production.body[0], Terminal):
                return False
        return True
