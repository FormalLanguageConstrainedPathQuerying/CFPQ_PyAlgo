import copy
import math
from typing import Tuple, Dict, Set, List, Iterable

import numba
import pygraphblas
from pygraphblas import types, select_op
from pygraphblas.binaryop import BinaryOp, binary_op
from pygraphblas.matrix import Matrix
from pathlib import Path
from copy import copy
from math import log2, ceil

from pygraphblas.selectop import SelectOp
from pygraphblas.types import Type


class TemplateRSA:
    """
    This class representing template for recursive state automaton with one nonterminal.

    Supports only the functions necessary for the tensor algorithm.
    """
    nonterms: Set[str]
    nonterm_via_eps: Set[str]
    start_states: Dict[str, int]
    finish_states: Dict[str, List[int]]
    transitions: List[Tuple[int, str, int]]
    template_paths: List[List[str]]
    states: Set[int]

    def __init__(self):
        """Initialize RSA with empty fields."""
        self.nonterms = set()
        self.start_states = dict()
        self.finish_states = dict()
        self.transitions = []
        self.template_paths = []
        self.states = set()

    def add_nonterm(self, nonterm: str, start_state: int, finish_states: Iterable[int]) -> None:
        """
        Add box to the RSA

        @param nonterm: box label
        @param start_state: start state of the box
        @param finish_states: collection of finish states of the box
        """
        self.nonterms.add(nonterm)
        self.states.add(start_state)
        self.start_states[nonterm] = start_state
        self.finish_states[nonterm] = list(finish_states)

    def add_edge(self, from_state: int, label: str, to_state: int) -> None:
        """
        Add labeled edge to the RSA

        @param from_state: source vertex of the edge
        @param label: edge label
        @param to_state: destination vertex of the edge
        """
        self.transitions.append((from_state, label, to_state))
        self.states.add(from_state)
        self.states.add(to_state)

    def add_template_path(self, path: Iterable[str]):
        self.template_paths.append(list(path))

    @classmethod
    def from_file(cls, path: Path):
        """
        Load OneNontermRSA from file.

        @param path: path to file with RSA
        @return: initialized TemplateRSA
        """
        rsa = cls()
        with open(path, "r") as file:
            nonterms_count = int(file.readline())
            for _ in range(nonterms_count):
                nonterm = file.readline().replace("\r", "").replace("\n", "")
                start_state = int(file.readline())
                finish_states = map(int, file.readline().replace("\r", "").replace("\n", "").split())
                rsa.add_nonterm(nonterm, start_state, finish_states)

            edges_count = int(file.readline())
            for _ in range(edges_count):
                from_s, label, to_s = file.readline().replace("\r", "").replace("\n", "").split(' ')
                from_s, to_s = int(from_s), int(to_s)
                rsa.add_edge(from_s, label, to_s)

            templ_edges_count = int(file.readline())
            for _ in range(templ_edges_count):
                rsa.add_template_path(file.readline().replace("\r", "").replace("\n", "").split(' '))
        return rsa


class OneTerminalRSA:
    start_state: Dict[str, int]
    finish_states: Dict[str, List[int]]
    nonterm_to_num: Dict[str, int]
    term_to_num: Dict[str, int]
    nonterm_via_eps: Set[str]
    matrix: Matrix
    times_op: BinaryOp
    select_op: SelectOp
    _nonterm_bits: int
    _term_bits: int

    def __init__(self,
                 states_count: int,
                 start_states: Dict[str, int],
                 finish_states: Dict[str, List[int]],
                 transitions: list[tuple[int, str, int]],
                 nonterm_to_num: Dict[str, int],
                 term_to_num: Dict[str, int]) -> None:

        self.start_state = copy(start_states)
        self.finish_states = copy(finish_states)

        self.nonterm_via_eps = set()
        self.nonterm_to_num = copy(nonterm_to_num)
        self.term_to_num = copy(term_to_num)

        for nonterm in self.nonterm_to_num:
            if self.start_state[nonterm] in self.finish_states[nonterm]:
                self.nonterm_via_eps.add(nonterm)

        self._term_bits = int(ceil(log2(len(term_to_num) + 1)))
        self._nonterm_bits = self._get_nonterm_bits()
        req_bits = self._term_bits + self._nonterm_bits

        if req_bits <= 8:
            element_size = 8
            element_type = types.UINT8
        elif req_bits <= 16:
            element_size = 16
            element_type = types.UINT16
        elif req_bits <= 32:
            element_size = 32
            element_type = types.UINT32
        elif req_bits <= 64:
            element_size = 64
            element_type = types.UINT64
        else:
            pass
        self._term_bits = element_size - self._nonterm_bits

        self.times_op = self._get_times_op(element_type, element_size)
        self.select_op = self._get_selector(element_type, element_type, element_size)

        self.matrix = Matrix.sparse(element_type, states_count, states_count)

        for from_s, label, to_s in transitions:
            value = self.matrix.get(from_s, to_s, default=0)
            if label in self.nonterm_to_num:
                self.matrix[from_s, to_s] = value | self.nonterm_to_matrix(label)
            else:
                self.matrix[from_s, to_s] = value | self.term_to_num[label]

    def nonterm_to_matrix(self, nonterm: str) -> int:
        """
        Convert non-terminal to its bit representation

        @param nonterm: non-terminal

        @return: mask for non-terminal
        """
        return 1 << (self._term_bits + self.nonterm_to_num[nonterm] - 1)

    def _get_nonterm_bits(self):
        return len(self.nonterm_to_num)

    def _get_times_op(self, argtype: Type, element_size: int) -> BinaryOp:
        term_mask = (1 << self._term_bits) - 1
        nonterm_mask = (1 << element_size) - 1 - term_mask

        def t(x, y):
            return ((x & y & nonterm_mask) != 0) or ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

        return binary_op(argtype)(t)

    def _get_selector(self, arg_type: Type, thunk_type: Type, element_size: int) -> SelectOp:

        def s(i, j, x, v):
            return x & nonterm_mask & v

        term_mask = (1 << self._term_bits) - 1
        nonterm_mask = (1 << element_size) - 1 - term_mask
        return select_op(arg_type, thunk_type)(s)

    @classmethod
    def from_template_rsa(cls,
                          template_rsa: TemplateRSA,
                          terms_nums: Set[int],
                          term_to_num: Dict[str, int]):
        """
        Create OneTerminalRSA from template RSA

        @param template_rsa:
        @param terms_nums: Terminal numbers to fill in template paths
        @param term_to_num: Terminals and their bit representation

        @return: initialized OneTerminalRSA
        """
        states_count = len(template_rsa.states)
        transitions = template_rsa.transitions.copy()
        terms_count = len(term_to_num)

        nonterm_to_num = dict()
        for i, nonterm in enumerate(template_rsa.nonterms):
            nonterm_to_num[nonterm] = i + 1

        for term_num in terms_nums:
            for temp_path in template_rsa.template_paths:
                from_s = int(temp_path[0])
                for i in range(len(temp_path) // 2):
                    if temp_path[2 * i + 1].find('[]') != -1:
                        label = temp_path[2 * i + 1] \
                            .replace('[]', str(term_num))
                        if label not in term_to_num:
                            term_to_num[label] = terms_count
                            terms_count += 1
                    else:
                        label = temp_path[2 * i + 1]
                    if temp_path[2 * i + 2] == '[]':
                        to_s = states_count
                        states_count += 1
                    else:
                        to_s = int(temp_path[2 * i + 2])
                    transitions.append((from_s, label, to_s))
                    from_s = to_s

        return cls(states_count,
                   template_rsa.start_states,
                   template_rsa.finish_states,
                   transitions,
                   nonterm_to_num,
                   term_to_num)
