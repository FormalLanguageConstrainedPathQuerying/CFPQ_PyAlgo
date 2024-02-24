from pathlib import Path
from typing import List, Tuple, Union


class Symbol:
    def __init__(self, label: str):
        self.label = label
        self.is_indexed = label.endswith('_i')

    def __repr__(self):
        return self.label

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self) -> int:
        return self.label.__hash__()


class CnfGrammarTemplate:
    def __init__(
        self,
        start_nonterm: Symbol,
        epsilon_rules: List[Symbol],
        simple_rules: List[Tuple[Symbol, Symbol]],
        complex_rules: List[Tuple[Symbol, Symbol, Symbol]]
    ):
        self.start_nonterm = start_nonterm
        self.epsilon_rules = epsilon_rules
        self.simple_rules = simple_rules
        self.complex_rules = complex_rules

        for (non_terminal, terminal) in simple_rules:
            if terminal in self.non_terminals:
                raise ValueError(f"Invalid rule '{non_terminal} {terminal}'. "
                                 f"Right hand side of a simple rule should be a terminal symbol.")

    @property
    def non_terminals(self):
        return set.union(
            set(self.epsilon_rules),
            (non_terminal for (non_terminal, _) in self.simple_rules),
            (non_terminal for (non_terminal, _, _) in self.complex_rules),
        )

    @staticmethod
    def read_from_pocr_cnf_file(path: Union[Path, str]) -> "CnfGrammarTemplate":
        """
        Reads a CNF grammar from a file and constructs a CnfGrammarTemplate object.

        The file format is expected to be as follows:
        - Each non-blank line represents a rule, except the last two lines.
        - Complex rules are in the format: <NON_TERMINAL> <SYMBOL_1> <SYMBOL_2>
        - Simple rules are in the format: <NON_TERMINAL> <TERMINAL>
        - Epsilon rules are in the format: <NON_TERMINAL>
        - Indexed symbols names must end with suffix '_i'.
        - Whitespace characters are used to separate values on one line
        - The last two lines specify the starting non-terminal in the format:
            '''
            Count:
            <START_NON_TERMINAL>
            '''
        """
        with open(path, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

            if len(lines) >= 2 and lines[-2] == "Count:":
                start_nonterm = Symbol(lines[-1])
                lines = lines[:-2]
            else:
                raise ValueError(
                    f"Invalid CNF grammar file '{path}'.\n"
                    f"The last two lines should specify the starting non-terminal in the format:\n"
                    f"'''\n"
                    f"Count:\n"
                    f"<START_NON_TERMINAL>\n"
                    f"'''"
                )

            epsilon_rules = []
            simple_rules = []
            complex_rules = []

            for line in lines:
                parts = line.split()
                if len(parts) == 1:
                    epsilon_rules.append(Symbol(parts[0]))
                elif len(parts) == 2:
                    simple_rules.append((Symbol(parts[0]), Symbol(parts[1])))
                elif len(parts) == 3:
                    complex_rules.append((Symbol(parts[0]), Symbol(parts[1]), Symbol(parts[2])))
                else:
                    raise ValueError(
                        f"Invalid rule format: '{line}' in file '{path}'. "
                        f"Expected formats are '<NON_TERMINAL> <SYMBOL_1> <SYMBOL_2>' for complex rules, "
                        f"'<NON_TERMINAL> <TERMINAL>' for simple rules, and '<NON_TERMINAL>' for epsilon rules."
                    )

            return CnfGrammarTemplate(start_nonterm, epsilon_rules, simple_rules, complex_rules)