from pygraphblas import *
from abc import ABC

from src.graph.label_graph import LabelGraph
from src.grammar.rsa import RecursiveAutomaton


class TensorSolver(ABC):
    def __init__(self, graph: LabelGraph, grammar: RecursiveAutomaton):
        self.graph = graph
        self.grammar = grammar
        for start in grammar.S():
            graph.matrices.update({start: Matrix.sparse(BOOL, graph.matrices_size, graph.matrices_size)})


class TensorAlgoSimple(TensorSolver):
    def __init__(self, graph: LabelGraph, grammar: RecursiveAutomaton):
        super().__init__(graph, grammar)

    def solve(self):
        for label in self.grammar.start_and_finish():
            for i in range(self.graph.matrices_size):
                self.graph[label][i, i] = True

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size()

        kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        control_sum = 0
        changed = True
        while changed:
            changed = False

            # calculate kronecker
            for label in self.grammar.labels():
                kron += self.grammar.automaton()[label].kron(self.graph[label])

            # transitive closer
            prev = kron.nvals
            degree = kron
            transitive_changed = True
            while transitive_changed:
                transitive_changed = False
                degree = degree @ kron
                kron += degree
                cur = kron.nvals
                if prev != cur:
                    prev = cur
                    transitive_changed = True

            # update
            for start in self.grammar.S():
                for element in self.grammar.states()[start]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size
                    block = kron[start_i:start_i + self.graph.matrices_size - 1,
                            start_j: start_j + self.graph.matrices_size - 1]

                    self.graph[start] += block
                    new_control_sum = self.graph[start].nvals

                    if new_control_sum != control_sum:
                        changed = True
                        control_sum = new_control_sum

        return control_sum, self.graph, kron
