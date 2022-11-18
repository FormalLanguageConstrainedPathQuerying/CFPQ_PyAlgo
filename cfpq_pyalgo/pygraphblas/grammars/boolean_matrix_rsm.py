"""Base class for Recursive State Machine decomposed into Boolean Matrices"""

from typing import Dict, List, Set, Tuple

from pyformlang.finite_automaton import State, Symbol
from pyformlang.rsa import Box, RecursiveAutomaton
from pygraphblas import Matrix

from cfpq_pyalgo.pygraphblas import BooleanMatrixGraph


class BooleanMatrixRsm:
    """A Recursive State Machine decomposed into Boolean Matrices class"""

    def __init__(
        self,
        transitions: BooleanMatrixGraph,
        labels: Set[str],
        nonterminals: Set[str],
        start_states: Dict[str, int],
        final_states: Dict[str, List[int]],
    ):
        self._labels: Set[str] = labels
        self._nonterminals: Set[str] = nonterminals
        self._transitions: BooleanMatrixGraph = transitions
        self._start_states: Dict[str, int] = start_states
        self._final_states: Dict[str, List[int]] = final_states

    def __getitem__(self, label: str) -> Matrix:
        return self._transitions[label]

    def __setitem__(self, label: str, matrix: Matrix):
        self._transitions[label] = matrix

    def __contains__(self, label: str) -> bool:
        return label in self._transitions

    @property
    def matrices_size(self) -> int:
        """The number of states in RSM

        Returns
        -------
        matrices_size: int
            Matrices size
        """
        return self._transitions.matrices_size

    @property
    def labels(self) -> Set[str]:
        """All RSM labels"""
        return self._labels

    @property
    def nonterminals(self) -> Set[str]:
        """Labels of boxes"""
        return self._nonterminals

    def add_edge(self, u: int, v: int, label: str) -> None:
        """Add an edge between `u` and `v` states with label `label.

        The states `u` and `v` will be automatically added if they are
        not already in the RSM.

        Parameters
        ----------
        u: int
            The tail of the edge

        v: int
            The head of the edge

        label: str
            The label of the edge
        """
        self._transitions.add_edge(u, v, label)

    def get_start_state(self, label: str) -> int:
        """Get start vertex for RSM box with label `label`

        Parameters
        ----------
        label: str
            The RSM box label

        Returns
        -------
        v: int
            Start vertex for the box
        """
        if label not in self._start_states:
            raise KeyError(f"{label}")
        return self._start_states[label]

    def set_start_vertex(self, label: str, v: int) -> None:
        """Set start vertex `v` for RSM box with label `label`

        Parameters
        ----------
        label: str
            The RSM box label

        v: int
            Start vertex for the box
        """
        self._start_states[label] = v

    def get_final_states(self, label: str) -> List[int]:
        """Get list of final vertices for RSM box with label `label`

        Parameters
        ----------
        label: str
            The RSM box label

        Returns
        -------
        vertices: List[int]
            List of final vertices for the box
        """
        if label not in self._final_states:
            raise KeyError(f"{label}")
        return self._final_states[label]

    def add_final_vertex(self, label: str, v: int):
        """Add final vertex `v` for RSM box with label `label`

        Parameters
        ----------
        label: str
            The RSM box label

        v: int
            Start vertex for the box
        """
        if label not in self._start_states:
            self._final_states[label] = [v]
        self._final_states[label].append(v)

    @classmethod
    def from_rsa(cls, rsa: RecursiveAutomaton) -> "BooleanMatrixRsm":
        """Create a BooleanMatrixRsa from RecursiveAutomaton `rsa`

        Parameters
        ----------
        rsa: RecursiveAutomaton
            RSM represented by pyformlang.rsa.RecursiveAutomaton class

        Returns
        -------
        boolean_matrix_rsa: BooleanMatrixRsm
            BooleanMatrixRsa constructed according to rsa
        """
        nonterminals: Set[str] = set()
        labels: Set[str] = set()
        start_states: Dict[str, int] = dict()
        final_states: Dict[str, List[int]] = dict()

        current_state = 0
        transition_by_label: Dict[str, List[Tuple[int, int]]] = dict()
        # Converting each box (states, transitions, start_state and final_states)
        for nonterminal, box in rsa.boxes.items():
            nonterminal_str: str = nonterminal.value
            nonterminals.add(nonterminal_str)
            box_symbols = list(map(lambda s: s.value, box.dfa.symbols))
            labels.update(box_symbols)
            for label in box_symbols:
                if label not in transition_by_label:
                    transition_by_label.update({label: []})
            # Map pyformlang states to numbers 0..states_count
            # and transitions between that states
            mapping_state: Dict[State, int] = dict()
            for state in box.dfa.states:
                if state not in mapping_state:
                    mapping_state[state] = current_state
                    current_state += 1
                dfa_dict: Dict[State, Dict[Symbol, State]] = box.dfa.to_dict()
                for transition in dfa_dict.get(state, dict()):
                    if dfa_dict[state][transition] not in mapping_state:
                        mapping_state[dfa_dict[state][transition]] = current_state
                        current_state += 1
                    transition_by_label[transition].append(
                        (
                            mapping_state[state],
                            mapping_state[dfa_dict[state][transition]],
                        )
                    )
            # Map start state and final states
            start_states[nonterminal_str] = mapping_state[box.dfa.start_state]
            final_states[nonterminal_str] = []
            for final_state in box.final_states:
                final_states[nonterminal_str].append(mapping_state[final_state])
        # Fill rsm transitions
        rsm_transitions: BooleanMatrixGraph = BooleanMatrixGraph(current_state)
        for label in transition_by_label:
            for transition in transition_by_label[label]:
                rsm_transitions.add_edge(transition[0], transition[1], label)

        rsm = cls(rsm_transitions, labels, nonterminals, start_states, final_states)
        return rsm
