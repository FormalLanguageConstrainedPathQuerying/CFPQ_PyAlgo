from pygraphblas import Matrix, BOOL
from pathlib import Path
from typing import Iterable

from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph
from src.problems.AllPaths.algo.tensor.tensor_path import TensorPaths

from src.problems.AllPaths.AllPaths import AllPathsProblem

from src.problems.utils import ResultAlgo


def restore_eps_paths(nonterminals: Iterable, graph: LabelGraph):
    for label in nonterminals:
        for i in range(graph.matrices_size):
            graph[label][i, i] = True


def transitive_closure(m: Matrix):
    prev = 0
    result = m.dup()
    while prev != result.nvals:
        prev = result.nvals
        result += result.mxm(result, semiring=BOOL.LOR_LAND)

    return result


class TensorSimpleAlgo(AllPathsProblem):

    def prepare(self, graph: Path, grammar: Path):
        self.graph = LabelGraph.from_txt(graph.with_suffix(".txt"))
        self.grammar = RecursiveAutomaton.from_file(grammar.with_suffix(".automat"))

    def solve(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        for label in self.grammar.nonterminals:
            self.graph[label].clear()

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        for label in self.grammar.labels:
            kron += self.grammar[label].kronecker(self.graph[label])

        iter = 0
        changed = True
        while changed:
            iter += 1
            changed = False

            for nonterminal in self.grammar.nonterminals:
                kron += self.grammar[nonterminal].kronecker(self.graph[nonterminal])

            kron_tc = transitive_closure(kron)

            # update
            for nonterminal in self.grammar.nonterminals:
                for element in self.grammar.states[nonterminal]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    control_sum = self.graph[nonterminal].nvals
                    block = kron_tc[start_i:start_i + self.graph.matrices_size - 1,
                                    start_j:start_j + self.graph.matrices_size - 1]

                    self.graph[nonterminal] += block
                    new_control_sum = self.graph[nonterminal].nvals

                    if new_control_sum != control_sum:
                        changed = True

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        self.kron = kron
        return ResultAlgo(self.graph["S"], iter)

    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        return TensorPaths(self.graph, self.grammar, self.kron).get_paths(v_start, v_finish, nonterminal, max_len)


class TensorDynamicAlgo(AllPathsProblem):

    def prepare(self, graph: Path, grammar: Path):
        self.graph = LabelGraph.from_txt(graph.with_suffix(".txt"))
        self.grammar = RecursiveAutomaton.from_file(grammar.with_suffix(".automat"))

    def solve(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        for label in self.grammar.nonterminals:
            self.graph[label].clear()

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        for label in self.grammar.labels:
            kron += self.grammar[label].kronecker(self.graph[label])

        prev_kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        iter = 0
        block = LabelGraph(self.graph.matrices_size)
        changed = True
        while changed:
            changed = False
            iter += 1
            for nonterminal in block.matrices:
                kron += self.grammar[nonterminal].kronecker(block[nonterminal])
                block[nonterminal] = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)

            kron_tc = transitive_closure(kron)
            part = prev_kron.mxm(kron_tc, semiring=BOOL.LOR_LAND)
            with BOOL.LOR_LAND:
                kron_tc += prev_kron + part @ prev_kron + part + kron_tc @ prev_kron

            prev_kron = kron_tc

            for nonterminal in self.grammar.nonterminals:
                for element in self.grammar.states[nonterminal]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    control_sum = self.graph[nonterminal].nvals
                    block[nonterminal] += kron_tc[start_i:start_i + self.graph.matrices_size - 1,
                                               start_j:start_j + self.graph.matrices_size - 1]

                    self.graph[nonterminal] += block[nonterminal]
                    print(block[nonterminal])
                    new_control_sum = self.graph[nonterminal].nvals

                    if new_control_sum != control_sum:
                        changed = True

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        self.kron = kron
        return ResultAlgo(self.graph["S"], iter)

    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        return TensorPaths(self.graph, self.grammar, self.kron).get_paths(v_start, v_finish, nonterminal, max_len)