from pygraphblas import Matrix, BOOL

from src.graph.graph import Graph
from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph


class TensorExtractSubGraph:
    def __init__(self, graph: Graph, rsa: RecursiveAutomaton, kron: Matrix, count_iter):
        self.graph = graph
        self.rsa = rsa
        self.kron = kron
        self.max_high = count_iter
        self.graph_size = graph.matrices_size

    def get_sub_graph(self, i, j, nonterm):
        return self.get_paths(i, j, nonterm, self.max_high)

    def get_paths(self, start, finish, nonterm, current_high):
        result = LabelGraph(self.graph_size)
        if current_high == 0:
            return result

        start_state = self.rsa.start_state[nonterm]

        for finish_state in self.rsa.finish_states[nonterm]:
            result += self.bfs(start_state * self.graph_size + start, finish_state * self.graph_size + finish, current_high, set())

        return result

    def bfs(self, i, j, current_high, visited_vertex):

        result_graph = LabelGraph(self.graph_size)
        for elem in self.kron[i]:
            if elem[0] in visited_vertex:
                continue
            else:
                visited_vertex.add(elem[0])
            graph_i = i % self.graph_size
            graph_j = elem[0] % self.graph_size

            rsa_i = i // self.graph_size
            rsa_j = elem[0] // self.graph_size

            left = LabelGraph(self.graph_size)
            for label in self.rsa.labels:
                if self.rsa[label].get(rsa_i, rsa_j, default=False):
                    if label in self.rsa.nonterminals:
                        left += self.get_paths(graph_i, graph_j, label, current_high - 1)
                    else:
                        if label not in left.matrices:
                            left.matrices[label] = Matrix.sparse(BOOL, self.graph_size, self.graph_size)
                        left.matrices[label][graph_i, graph_j] = True

            if left.is_empty:
                continue

            right = LabelGraph(self.graph_size)
            if elem[0] != j:
                right = self.bfs(elem[0], j, current_high, visited_vertex)
            else:
                right.matrices[self.rsa.start_nonterm] = Matrix.sparse(BOOL, self.graph_size, self.graph_size)

            if right.is_empty:
                continue

            result_graph += left + right

        return result_graph
