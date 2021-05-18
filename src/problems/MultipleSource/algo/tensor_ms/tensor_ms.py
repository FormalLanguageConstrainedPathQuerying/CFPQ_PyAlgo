from pathlib import Path
from typing import Iterable

from pygraphblas import Matrix, BOOL

from src.problems.MultipleSource.MultipleSource import MultipleSourceProblem

from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph

from src.problems.AllPaths.algo.tensor.tensor import restore_eps_paths, transitive_closure
from src.problems.utils import ResultAlgo


class TensorMSAlgo(MultipleSourceProblem):

    def prepare(self, graph: Path, grammar: Path):
        self.graph = LabelGraph.from_txt(graph.with_suffix(".txt"))
        self.grammar = RecursiveAutomaton.from_file(grammar.with_suffix(".automat"))
        self.part_graph = LabelGraph(self.graph.matrices_size)
        self.src_for_states = dict()
        for i in range(self.grammar.matrices_size):
            self.src_for_states.update({i: Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)})

    def solve(self, sources: Iterable):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        for v in sources:
            self.src_for_states[self.grammar.start_state["S"]][v, v] = True

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        kron = Matrix.sparse(BOOL, sizeKron, sizeKron)

        changed = True
        src_changed = True
        iter = 0
        while changed or src_changed:
            iter += 1
            changed = False
            src_changed = False

            for state in range(self.grammar.matrices_size):
                out_state = self.grammar.out_states.get(state, [])
                for out in out_state:
                    if out[1] == "S":
                        old_sum = self.src_for_states[self.grammar.start_state["S"]].nvals
                        self.src_for_states[self.grammar.start_state["S"]] += self.src_for_states[state]
                        if old_sum != self.src_for_states[self.grammar.start_state["S"]].nvals:
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

            kron_tc = transitive_closure(kron)

            for start in self.grammar.nonterminals:
                for element in self.grammar.states[start]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    control_sum = self.graph[start].nvals
                    block = kron_tc[start_i:start_i + self.graph.matrices_size - 1,
                            start_j: start_j + self.graph.matrices_size - 1]

                    self.graph[start] += block
                    new_control_sum = self.graph[start].nvals

                    if new_control_sum != control_sum:
                        changed = True

        return ResultAlgo(self.graph["S"], iter)
