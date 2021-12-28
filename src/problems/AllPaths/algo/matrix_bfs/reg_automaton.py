from __future__ import annotations

from pyformlang.regular_expression.regex import Regex

from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL


class RegAutomaton:
    """
    Automata representation of regular grammar
    """

    def __init__(self, regex: Regex):
        self.enfa = regex.to_epsilon_nfa().minimize()

        self.states = self.enfa.states
        self.num_states = len(self.states)

        self.enum_states = dict(zip(self.states, range(self.num_states)))
        self.start_states = [
            self.enum_states[state] for state in self.enfa.start_states
        ]
        self.final_states = [
            self.enum_states[state] for state in self.enfa.final_states
        ]

        self.matrices = dict()
        self.load_bool_matrices()

    def from_regex_txt(path) -> RegAutomaton:
        with open(path, "r") as file:
            regex = Regex(file.readline())

            return RegAutomaton(regex)

    def load_bool_matrices(self) -> None:
        """
        Creates boolean matrices for self automata
        """
        for src_node, transition in self.enfa.to_dict().items():
            for symbol, tgt_node in transition.items():
                if symbol not in self.matrices:
                    self.matrices[symbol] = Matrix.sparse(
                        BOOL, self.num_states, self.num_states
                    )

                matr = self.matrices[symbol]
                matr[self.enum_states[src_node], self.enum_states[tgt_node]] = True
