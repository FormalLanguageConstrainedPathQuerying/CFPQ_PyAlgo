from pathlib import Path
from cfpq_data import RSM
from pyformlang.cfg import CFG
from src.graph.graph import Graph
from typing import Iterable, Union

from pygraphblas import Matrix, BOOL

from src.problems.MultipleSource.MultipleSource import MultipleSourceProblem

from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph

from src.problems.AllPaths.algo.tensor.tensor import restore_eps_paths, transitive_closure
from src.problems.utils import ResultAlgo


class TensorMSAlgo(MultipleSourceProblem):

    def prepare(self, graph: Graph, grammar: Union[RSM, CFG, Path]):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = RecursiveAutomaton.from_grammar_or_path(grammar)
        self.part_graph = LabelGraph(self.graph.matrices_size)
        self.src_for_states = dict()
        for i in range(self.grammar.matrices_size):
            self.src_for_states.update({i: Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)})

    def clear_src(self):
        for label in self.src_for_states:
            self.src_for_states[label].clear()

        for nonterm in self.grammar.nonterminals:
            self.graph[nonterm].clear()

    def solve(self, sources: Iterable):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        # Initialize source matrices masks
        m_src = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
        for v in sources:
            m_src[v, v] = True
            self.src_for_states[self.grammar.start_state[self.grammar.start_nonterm]][v, v] = True

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        kron = Matrix.sparse(BOOL, sizeKron, sizeKron)

        changed = True
        src_changed = True
        iter = 0
        while changed or src_changed:
            iter += 1
            changed = False
            src_changed = False

            for box in self.grammar.boxes:
                for state in self.grammar.boxes[box]:
                    out_state = self.grammar.out_states.get(state, [])
                    for out in out_state:
                        if out[1] in self.grammar.nonterminals:
                            old_sum = self.src_for_states[self.grammar.start_state[out[1]]].nvals
                            self.src_for_states[self.grammar.start_state[out[1]]] += self.src_for_states[state]
                            if old_sum != self.src_for_states[self.grammar.start_state[out[1]]].nvals:
                                src_changed = True
                        with BOOL.LOR_LAND:
                            self.part_graph[out[1]] += self.src_for_states[state].mxm(self.graph[out[1]])
                        old_sum = self.src_for_states[out[0]].nvals
                        for elem in self.part_graph[out[1]].T.reduce_vector(BOOL.LAND_MONOID):
                            self.src_for_states[out[0]][elem[0], elem[0]] = True
                        if old_sum != self.src_for_states[out[0]].nvals:
                            src_changed = True

            for label in self.grammar.labels:
                kron += self.grammar[label].kronecker(self.part_graph[label])

            transitive_closure(kron)

            for start in self.grammar.nonterminals:
                for element in self.grammar.states[start]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    control_sum = self.graph[start].nvals
                    block = kron[start_i:start_i + self.graph.matrices_size - 1,
                                 start_j: start_j + self.graph.matrices_size - 1]

                    self.graph[start] += block
                    new_control_sum = self.graph[start].nvals

                    if new_control_sum != control_sum:
                        changed = True

        return ResultAlgo(m_src.mxm(self.graph[self.grammar.start_nonterm], semiring=BOOL.LOR_LAND), iter)


class TensorMSAllAlgo(MultipleSourceProblem):

    def prepare(self, graph: Graph, grammar: Union[RSM, CFG, Path]):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = RecursiveAutomaton.from_grammar_or_path(grammar)
        self.part_graph = LabelGraph(self.graph.matrices_size)
        self.src_for_states = dict()
        for i in range(self.grammar.matrices_size):
            self.src_for_states.update({i: Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)})

    def clear_src(self):
        for label in self.src_for_states:
            self.src_for_states[label].clear()

        for nonterm in self.grammar.nonterminals:
            self.graph[nonterm].clear()

    def solve(self, sources: Iterable):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        for v in sources:
            self.src_for_states[self.grammar.start_state[self.grammar.start_nonterm]][v, v] = True

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        kron = Matrix.sparse(BOOL, sizeKron, sizeKron)

        changed = True
        iter = 0
        while changed:
            iter += 1
            changed = False
            src_changed = True
            while src_changed:
                src_changed = False
                for box in self.grammar.boxes:
                    for state in self.grammar.boxes[box]:
                        out_state = self.grammar.out_states.get(state, [])
                        for out in out_state:
                            if out[1] in self.grammar.nonterminals:
                                old_sum = self.src_for_states[self.grammar.start_state[out[1]]].nvals
                                self.src_for_states[self.grammar.start_state[out[1]]] += self.src_for_states[state]
                                if old_sum != self.src_for_states[self.grammar.start_state[out[1]]].nvals:
                                    src_changed = True
                            with BOOL.LOR_LAND:
                                self.part_graph[out[1]] += self.src_for_states[state].mxm(self.graph[out[1]])
                            old_sum = self.src_for_states[out[0]].nvals
                            for elem in self.part_graph[out[1]].T.reduce_vector(BOOL.LAND_MONOID):
                                self.src_for_states[out[0]][elem[0], elem[0]] = True
                            if old_sum != self.src_for_states[out[0]].nvals:
                                src_changed = True

            for label in self.grammar.labels:
                kron += self.grammar[label].kronecker(self.part_graph[label])

            transitive_closure(kron)

            for start in self.grammar.nonterminals:
                for element in self.grammar.states[start]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    control_sum = self.graph[start].nvals
                    block = kron[start_i:start_i + self.graph.matrices_size - 1,
                                 start_j: start_j + self.graph.matrices_size - 1]

                    self.graph[start] += block
                    new_control_sum = self.graph[start].nvals

                    if new_control_sum != control_sum:
                        changed = True

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)