from pygraphblas import Matrix, BOOL

from src.graph.graph import Graph
from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph


class TensorExtractSubGraph:

    def __init__(self, graph: Graph, rsa: RecursiveAutomaton, kron: Matrix):
        self.graph = graph
        self.rsa = rsa
        self.kron = kron
        self.graph_size = graph.matrices_size
        self.solved_triplets = set()
        self.visited_pairs_in_kron = set()
        self.negative_visited_in_kron = set()

    def get_sub_graph(self, i, j, nonterm):
        return self.get_paths(i, j, nonterm)

    def get_paths(self, start, finish, nonterm):

        if (start, finish, nonterm) in self.solved_triplets:
            bogus_result = LabelGraph(self.graph_size)
            bogus_result.is_empty = False
            return bogus_result

        self.solved_triplets.add((start, finish, nonterm))

        result = LabelGraph(self.graph_size)
        start_state = self.rsa.start_state[nonterm]

        for finish_state in self.rsa.finish_states[nonterm]:
            result += self.bfs(start_state * self.graph_size + start, finish_state * self.graph_size + finish)

        self.solved_triplets.remove((start, finish, nonterm))

        return result

    def bfs(self, i, j):

        if (i, j) in self.negative_visited_in_kron:
            return LabelGraph(self.graph_size)

        if (i, j) in self.visited_pairs_in_kron:
            bogus_result = LabelGraph(self.graph_size)
            bogus_result.is_empty = False
            return bogus_result
        self.visited_pairs_in_kron.add((i, j))

        result_graph = LabelGraph(self.graph_size)
        for k in self.kron[i]:  # k = (vertex, True)
            graph_i = i % self.graph_size
            graph_k = k[0] % self.graph_size

            rsa_i = i // self.graph_size
            rsa_k = k[0] // self.graph_size

            left = LabelGraph(self.graph_size)
            for label in self.rsa.labels:
                if self.rsa[label].get(rsa_i, rsa_k, default=False):
                    if label in self.rsa.nonterminals:
                        left += self.get_paths(graph_i, graph_k, label)
                    else:
                        if label not in left.matrices:
                            left[label] = Matrix.sparse(BOOL, self.graph_size, self.graph_size)
                        left[label][graph_i, graph_k] = True

            if left.is_empty:
                continue

            right = LabelGraph(self.graph_size)
            if k[0] != j:
                right = self.bfs(k[0], j)
            else:
                right.is_empty = False

            if right.is_empty:
                continue

            result_graph += left + right

        if result_graph.is_empty:
            self.negative_visited_in_kron.add((i, j))

        self.visited_pairs_in_kron.remove((i, j))

        return result_graph
