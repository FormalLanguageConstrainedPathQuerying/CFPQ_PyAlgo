from typing import Tuple, Dict, Set, List
from pyformlang.finite_automaton.deterministic_finite_automaton import DeterministicFiniteAutomaton
from pygraphblas import types

from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL

from pathlib import Path

from pyformlang.cfg import CFG
from cfpq_data import rsm_from_text
from cfpq_data.grammars.rsm import RSM

NONTERMINAL_MASK_INT32 = 0x80000000
MAX_TERMINALS_COUNT_INT32 = 0x7fffffff

NONTERMINAL_MASK_INT64 = 0x8000000000000000
MAX_TERMINALS_COUNT_INT64 = 0x7fffffffffffff


class TemplateRSA:
    """
    This class representing recursive state automaton with one nonterminal.

    Supports only the functions necessary for the tensor algorithm.
    """

    def __init__(self):
        """Initialize RSA with empty fields."""
        self.labels: Set[str] = set()
        self.nonterms: Set[str] = set()
        self.nonterm_via_eps: Set[str] = set()
        self.start_state: Dict[str, int] = dict()
        self.finish_states: Dict[str, List[int]] = dict()
        self.edges: List[Tuple[int, str, int]] = []
        self.template_paths: List[List[str]] = []
        self.states: Set[int] = set()
        self.nonterm_to_num: Dict[str, int] = dict()

    @classmethod
    def from_file(cls, path: Path):
        """
        Load OneNontermRSA from file.

        @param path: path to file with RSA
        @return: initialized TemplateRSA
        """
        rsa = TemplateRSA()
        with open(path, "r") as file:
            nonterms_count = int(file.readline())
            nonterm_num = 1
            for _ in range(nonterms_count):
                nonterm = file.readline().replace("\r", "").replace("\n", "")
                rsa.nonterms.add(nonterm)
                rsa.nonterm_to_num[nonterm] = nonterm_num
                nonterm_num += 1
                rsa.start_state[nonterm] = int(file.readline())
                rsa.finish_states[nonterm] = list(
                    map(int, file.readline().replace("\r", "").replace("\n", "").split()))
                if rsa.start_state[nonterm] in rsa.finish_states[nonterm]:
                    rsa.nonterm_via_eps.add(nonterm)

            edges_count = int(file.readline())
            for _ in range(edges_count):
                from_s, label, to_s = file.readline().replace(
                    "\r", "").replace("\n", "").split(' ')
                from_s, to_s = int(from_s), int(to_s)
                rsa.edges.append((from_s, label, to_s))
                rsa.states.add(from_s)
                rsa.states.add(to_s)

            templ_edges_count = int(file.readline())
            for _ in range(templ_edges_count):
                rsa.template_paths.append(file.readline().replace(
                    "\r", "").replace("\n", "").split(' '))
        return rsa


class OneTerminalOneNonterminalRSA:

    def __init__(self, template_rsa: TemplateRSA, element_type, element_size, terms_nums, terminals_to_num) -> None:
        self.start_state = template_rsa.start_state
        self.finish_states = template_rsa.finish_states
        self.nonterm_to_num = template_rsa.nonterm_to_num
        self.nonterm_via_eps = template_rsa.nonterm_via_eps

        states_count = len(template_rsa.states)
        edges = template_rsa.edges.copy()
        terms_count = len(terminals_to_num)
        for term_num in terms_nums:
            for temp_path in template_rsa.template_paths:
                from_s = int(temp_path[0])
                for i in range(len(temp_path) // 2):
                    if temp_path[2 * i + 1].find('[]') != -1:
                        label = temp_path[2 * i + 1] \
                            .replace('[]', str(term_num))
                        if label not in terminals_to_num:
                            terminals_to_num[label] = terms_count
                            terms_count += 1
                    else:
                        label = temp_path[2 * i + 1]
                    if temp_path[2 * i + 2] == '[]':
                        to_s = states_count
                        states_count += 1
                    else:
                        to_s = int(temp_path[2 * i + 2])
                    edges.append((from_s, label, to_s))
                    from_s = to_s

        self.matrix = Matrix.sparse(
            element_type, states_count, states_count)
        for from_s, label, to_s in edges:
            value = self.matrix.get(from_s, to_s, default=0)
            if label in self.nonterm_to_num:
                self.matrix[from_s, to_s] = value | self.nonterm_to_num[label] << (element_size - 2)
            else:
                self.matrix[from_s, to_s] = value | terminals_to_num[label]


class OneTerminalRSA:

    def __init__(self, template_rsa: TemplateRSA, element_type, element_size, terms_nums, terminals_to_num) -> None:
        self.start_state = template_rsa.start_state
        self.finish_states = template_rsa.finish_states
        self.nonterm_to_num = template_rsa.nonterm_to_num
        self.nonterm_via_eps = template_rsa.nonterm_via_eps

        states_count = len(template_rsa.states)
        edges = template_rsa.edges.copy()
        terms_count = len(terminals_to_num)
        for term_num in terms_nums:
            for temp_path in template_rsa.template_paths:
                from_s = int(temp_path[0])
                for i in range(len(temp_path) // 2):
                    if temp_path[2 * i + 1].find('[]') != -1:
                        label = temp_path[2 * i + 1] \
                            .replace('[]', str(term_num))
                        if label not in terminals_to_num:
                            terminals_to_num[label] = terms_count
                            terms_count += 1
                    else:
                        label = temp_path[2 * i + 1]
                    if temp_path[2 * i + 2] == '[]':
                        to_s = states_count
                        states_count += 1
                    else:
                        to_s = int(temp_path[2 * i + 2])
                    edges.append((from_s, label, to_s))
                    from_s = to_s

        self.matrix = Matrix.sparse(
            element_type, states_count, states_count)
        for from_s, label, to_s in edges:
            value = self.matrix.get(from_s, to_s, default=0)
            if label in self.nonterm_to_num:
                self.matrix[from_s, to_s] = value | 1 << (element_size - 3 + self.nonterm_to_num[label] - 1)
            else:
                self.matrix[from_s, to_s] = value | terminals_to_num[label]

