from pathlib import Path
from cfpq_data import RSM
from pyformlang.cfg import CFG
from pygraphblas import Matrix, BOOL, Vector, descriptor
from src.graph.graph import Graph
from typing import Iterable, Union

from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph
from src.problems.AllPaths.algo.tensor.tensor_path import TensorPathsNew
from src.problems.AllPaths.algo.tensor.tensor_extract_subgraph import TensorExtractSubGraph

from src.problems.AllPaths.AllPaths import AllPathsProblem

from src.problems.utils import ResultAlgo


def restore_eps_paths(nonterminals: Iterable, graph: Graph):
    for label in nonterminals:
        for i in range(graph.matrices_size):
            graph[label][i, i] = True


# def transitive_closure(m: Matrix):
#     prev = -1
#     while prev != m.nvals:
#         prev = m.nvals
#         with BOOL.ANY_PAIR, Accum(BOOL.ANY):
#             m @= m

def transitive_closure(m: Matrix):
    prev = m.nvals
    degree = m
    with BOOL.ANY_PAIR:
        degree = degree @ m
        m += degree
    while prev != m.nvals:
        prev = m.nvals
        with BOOL.ANY_PAIR:
            degree = degree @ m
            m += degree


def ms_bfs(sources: Matrix, kron: Matrix, visited: Matrix):
    with BOOL.ANY_PAIR:
        front = visited @ sources
        while front.nvals > 0:
            new_front = front.mxm(kron)
            front = new_front.union(visited, mask=visited, desc=descriptor.C)
            visited += front


class TensorSimpleAlgo(AllPathsProblem):

    def prepare(self, graph: Graph, grammar: Union[RSM, CFG, Path]):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = RecursiveAutomaton.from_grammar_or_path(grammar)

    def solve(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        iter = 0
        changed = True
        while changed:
            iter += 1
            changed = False

            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
            for label in self.grammar.labels:
                kron += self.grammar[label].kronecker(self.graph[label])

            transitive_closure(kron)

            # update
            for nonterminal in self.grammar.nonterminals:
                control_sum = self.graph[nonterminal].nvals
                for element in self.grammar.states[nonterminal]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    self.graph[nonterminal] += kron[start_i:start_i + self.graph.matrices_size - 1,
                            start_j:start_j + self.graph.matrices_size - 1]

                new_control_sum = self.graph[nonterminal].nvals

                if new_control_sum != control_sum:
                    changed = True

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)

    def prepare_for_solve(self):
        for label in self.grammar.nonterminals:
            self.graph[label].clear()

    def prepare_for_exctract_paths(self):
        sizeKron = self.graph.matrices_size * self.grammar.matrices_size
        self.kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        for label in self.grammar.labels:
            self.kron += self.grammar[label].kronecker(self.graph[label])

    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        return TensorPathsNew(self.graph, self.grammar, self.kron).get_paths(v_start, v_finish, nonterminal, max_len)

    def get_sub_graph(self, v_start: int, v_finish: int, nonterminal: str, max_high: int):
        return TensorExtractSubGraph(self.graph, self.grammar, self.kron, max_high).get_sub_graph(v_start,
                                                                                                  v_finish,
                                                                                                  nonterminal)


class TensorDynamicAlgo(AllPathsProblem):

    def prepare(self, graph: Graph, grammar: Union[RSM, CFG, Path]):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = RecursiveAutomaton.from_grammar_or_path(grammar)

    def solve(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        graph_size = self.graph.matrices_size
        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        prev_kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        iter = 0
        block = LabelGraph(self.graph.matrices_size)
        changed = True
        first_iter = True
        start_states = [self.grammar.start_state[nonterm] for nonterm in self.grammar.nonterminals]
        while changed:
            changed = False
            iter += 1

            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)

            if first_iter:
                for label in self.grammar.labels:
                    kron += self.grammar[label].kronecker(self.graph[label])
                graph_diag = Matrix.from_diag(Vector.dense(BOOL, graph_size, fill=True))
                ms_bfs_sources = Matrix.sparse(BOOL, nrows=kron.ncols, ncols=kron.ncols)
                for v in start_states:
                    start = v * graph_size
                    ms_bfs_sources[start: start + graph_size - 1, start:start + graph_size - 1] = graph_diag
                ms_bfs_visited = ms_bfs_sources.dup()
                ms_bfs(ms_bfs_sources, kron, ms_bfs_visited)
                prev_kron = kron
                visited_updates = ms_bfs_visited.dup()

            else:
                for nonterminal in block.matrices:
                    kron += self.grammar[nonterminal].kronecker(block[nonterminal])
                    block[nonterminal] = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
                ms_bfs_sources = Matrix.from_diag(kron.reduce_vector())
                with BOOL.ANY_PAIR:
                    kron = prev_kron + kron
                visited_updates = ms_bfs_visited.dup()
                ms_bfs(ms_bfs_sources, kron, ms_bfs_visited)
                visited_updates = (ms_bfs_visited - visited_updates).nonzero()
                prev_kron = kron

            for nonterminal in self.grammar.nonterminals:
                control_sum = self.graph[nonterminal].nvals
                for element in self.grammar.states[nonterminal]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    # block[nonterminal] += kron[start_i:start_i + self.graph.matrices_size - 1,
                    #                       start_j:start_j + self.graph.matrices_size - 1]
                    if first_iter:
                        block[nonterminal] += visited_updates[start_i:start_i + self.graph.matrices_size - 1,
                                                  start_j:start_j + self.graph.matrices_size - 1]
                    else:
                        new_edges = visited_updates[start_i:start_i + self.graph.matrices_size - 1,
                                         start_j:start_j + self.graph.matrices_size - 1]
                        part = new_edges - block[nonterminal]
                        block[nonterminal] += part.select('==', True)

                self.graph[nonterminal] += block[nonterminal]
                new_control_sum = self.graph[nonterminal].nvals

                if new_control_sum != control_sum:
                    changed = True

            first_iter = False

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)

    def prepare_for_solve(self):
        for label in self.grammar.nonterminals:
            self.graph[label].clear()

    def prepare_for_exctract_paths(self):
        sizeKron = self.graph.matrices_size * self.grammar.matrices_size
        self.kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        for label in self.grammar.labels:
            self.kron += self.grammar[label].kronecker(self.graph[label])

    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        return TensorPathsNew(self.graph, self.grammar, self.kron).get_paths(v_start, v_finish, nonterminal, max_len)

    def get_sub_graph(self, v_start: int, v_finish: int, nonterminal: str, max_high: int):
        return TensorExtractSubGraph(self.graph, self.grammar, self.kron, max_high).get_sub_graph(v_start,
                                                                                                  v_finish,
                                                                                                  nonterminal)
