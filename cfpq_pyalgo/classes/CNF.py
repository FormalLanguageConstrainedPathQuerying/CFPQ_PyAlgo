from typing import AbstractSet, Iterable

from cfpq_data import cnf_from_cfg
from pyformlang.cfg import CFG, Variable, Terminal, Production

__all__ = [
    "CNF",
]


class CNF:
    def __init__(self,
                 start_symbol: Variable,
                 variables: AbstractSet[Variable],
                 terminals: AbstractSet[Terminal],
                 unary_productions: Iterable[Production],
                 double_productions: Iterable[Production],
                 ):
        self.start_symbol = start_symbol
        self.variables = variables
        self.terminals = terminals
        self.unary_productions = unary_productions
        self.double_productions = double_productions

    @classmethod
    def from_cfg(cls, cfg: CFG):
        base_cnf = cnf_from_cfg(cfg)

        cnf = CNF(
            base_cnf.start_symbol,
            base_cnf.variables,
            base_cnf.terminals,
            [p for p in base_cnf.productions if len(p.body) == 1],
            [p for p in base_cnf.productions if len(p.body) == 2]
        )

        return cnf
