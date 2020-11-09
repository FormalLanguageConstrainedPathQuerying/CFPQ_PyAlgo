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
        count_tc = 0
        first_iter = True
        changed = True
        while changed:
            changed = False

            # calculate kronecker
            for label in self.grammar.labels():
                with semiring.LOR_LAND_BOOL:
                    kron += self.grammar.automaton()[label].kron(self.graph[label])

            kron.select(lib.GxB_NONZERO)

            # transitive closer
            prev = kron.nvals
            degree = kron
            transitive_changed = True
            while transitive_changed:
                if first_iter:
                    count_tc += 1
                transitive_changed = False
                with semiring.LOR_LAND_BOOL:
                    degree = degree @ kron
                degree.select(lib.GxB_NONZERO)
                with semiring.LOR_LAND_BOOL:
                    kron += degree
                cur = kron.nvals
                if prev != cur:
                    prev = cur
                    transitive_changed = True

            first_iter = False

            kron.select(lib.GxB_NONZERO)

            # update
            for start in self.grammar.S():
                for element in self.grammar.states()[start]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size
                    block = kron[start_i:start_i + self.graph.matrices_size - 1, start_j: start_j + self.graph.matrices_size - 1]
                    block.select(lib.GxB_NONZERO)

                    with semiring.LOR_LAND_BOOL:
                        self.graph[start] += block
                        self.graph[start].select(lib.GxB_NONZERO)
                    new_control_sum = self.graph[start].nvals

                    if new_control_sum != control_sum:
                        changed = True
                        control_sum = new_control_sum

        return control_sum, self.graph, kron, count_tc
