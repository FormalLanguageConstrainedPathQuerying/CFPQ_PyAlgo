from pygraphblas import Matrix, BOOL
from pathlib import Path

from src.algo.algo_interface import CFPQAlgo

from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph


class TensorSolver(CFPQAlgo):

    def __init__(self, path_to_graph: Path, path_to_grammar: Path):
        super().__init__(path_to_graph, path_to_grammar)
        self.graph = LabelGraph.from_txt(str(path_to_graph) + ".txt")
        self.grammar = RecursiveAutomaton.from_file(str(path_to_grammar) + ".automat")

    def solve(self):
        pass


class TensorAlgoSimple(TensorSolver):

    def solve(self):

        for label in self.grammar.start_and_finish():
            for i in range(self.graph.matrices_size):
                self.graph[label][i, i] = True

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size()

        kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        changed = True
        while changed:
            changed = False

            # calculate kronecker
            for label in self.grammar.labels():
                kron += self.grammar.automaton()[label].kronecker(self.graph[label])

            # transitive closure
            prev = kron.nvals
            degree = kron
            transitive_changed = True
            while transitive_changed:
                transitive_changed = False
                degree = degree.mxm(kron, semiring=BOOL.LOR_LAND)
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

                    control_sum = self.graph[start].nvals
                    block = kron[start_i:start_i + self.graph.matrices_size - 1,
                            start_j: start_j + self.graph.matrices_size - 1]

                    self.graph[start] += block
                    new_control_sum = self.graph[start].nvals

                    if new_control_sum != control_sum:
                        changed = True

            if self.grammar.S().isdisjoint(self.grammar.labels()):
                break

        return self.graph


class TensorAlgoDynamic(TensorSolver):

    def solve(self):

        for label in self.grammar.start_and_finish():
            for i in range(self.graph.matrices_size):
                self.graph[label][i, i] = True

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size()

        prev_kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        block = dict()
        for label in self.grammar.S():
            block.update({label: Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)})

        first_iter = True
        changed = True
        while changed:
            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
            changed = False

            # calculate kronecker
            if first_iter:
                for label in self.grammar.labels():
                    kron += self.grammar.automaton()[label].kronecker(self.graph[label])
            else:
                for label in self.grammar.S():
                    kron += self.grammar.automaton()[label].kronecker(block[label])

            if not first_iter:
                for label in self.grammar.S():
                    block.update({label: Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)})

            # transitive closure
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

            if not first_iter:
                part = prev_kron.mxm(kron, semiring=BOOL.LOR_LAND)
                with BOOL.LOR_LAND:
                    kron = prev_kron + part @ prev_kron + part + kron @ prev_kron + kron

            prev_kron = kron
            first_iter = False

            # update
            for start in self.grammar.S():
                for element in self.grammar.states()[start]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    control_sum = self.graph[start].nvals
                    block[start] += kron[start_i:start_i + self.graph.matrices_size - 1,
                                    start_j: start_j + self.graph.matrices_size - 1]

                    self.graph[start] += block[start]
                    new_control_sum = self.graph[start].nvals

                    if new_control_sum != control_sum:
                        changed = True

            if self.grammar.S().isdisjoint(self.grammar.labels()):
                break

        return self.graph
