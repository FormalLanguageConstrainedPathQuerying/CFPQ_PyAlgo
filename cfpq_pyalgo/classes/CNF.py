from typing import AbstractSet, Iterable, Tuple

from cfpq_data import cnf_from_cfg
from pyformlang.cfg import CFG, Variable, Terminal

__all__ = [
    "CNF",
]


class CNF:
    def __init__(
        self,
        start_symbol: Variable,
        variables: AbstractSet[Variable],
        terminals: AbstractSet[Terminal],
        unary_productions: Iterable[Tuple[Variable, Terminal]],
        double_productions: Iterable[Tuple[Variable, Variable, Variable]],
    ):
        self.start_symbol = start_symbol
        self.variables = variables
        self.terminals = terminals
        self.unary_productions = unary_productions
        self.double_productions = double_productions

    @classmethod
    def from_cfg(cls, cfg: CFG):
        base_cnf = cnf_from_cfg(cfg)

        unary_productions = list()
        double_productions = list()

        for p in base_cnf.productions:
            if len(p.body) == 0:
                unary_productions.append((p.head, Terminal("$")))
            elif len(p.body) == 1:
                unary_productions.append((p.head, Terminal(p.body[0].value)))
            elif len(p.body) == 2:
                double_productions.append(
                    (p.head, Variable(p.body[0].value), Variable(p.body[1].value))
                )

        cnf = CNF(
            base_cnf.start_symbol,
            base_cnf.variables,
            base_cnf.terminals,
            unary_productions,
            double_productions,
        )

        return cnf

    @classmethod
    def from_text(cls, text, start_symbol: Variable = Variable("S")):
        return CNF.from_cfg(CFG.from_text(text, start_symbol))
