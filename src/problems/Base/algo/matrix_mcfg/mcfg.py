from pygraphblas import Matrix, BOOL
from typing import List

from src.graph.graph import Graph
from src.grammar.mcfg import MCFG


class MatrixBaseMCFG:
    def __init__(self, graph: Graph, grammar: MCFG):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = grammar
        self.max_indices = sum([(self.graph.matrices_size + 1) * ((self.graph.matrices_size + 1) ** (j - 1)) for j in
                                range(1, 2 * self.grammar.m + 1)])
        self.M = {N: Matrix.sparse(BOOL, self.max_indices, self.max_indices) for N in self.grammar.nonterminals}

    def get_element_of_V(self, value):
        if value == 0:
            return [0]
        result = []
        while value > 0:
            result += [value % (self.graph.matrices_size + 1)]
            value //= self.graph.matrices_size + 1
        return result

    def solve(self):
        for A, r_rules in self.grammar.terminal_rules.items():
            for p in r_rules:
                indices_to_add: List[List[int]] = []
                check = False

                for elem in self.graph[p[0]]:
                    indices_to_add.append([elem[0], elem[1]])
                new_indices_for_a = []
                for i in range(len(indices_to_add)):
                    for a in p[1:]:
                        if self.graph[a].nvals == 0:
                            check = True
                            break
                        for elem in self.graph[a]:
                            new_indices_for_a.append(indices_to_add[i] + [elem[0]] + [elem[1]])
                if len(new_indices_for_a) != 0:
                    indices_to_add = new_indices_for_a

                if not check:
                    for indices in indices_to_add:
                        left = indices[:len(indices) // 2]
                        right = indices[len(indices) // 2:]
                        first_index = sum(left[j] * ((self.graph.matrices_size + 1) ** j) for j in range(len(left)))
                        second_index = sum(right[j] * ((self.graph.matrices_size + 1) ** j) for j in range(len(right)))
                        self.M[A][first_index, second_index] = True

        M_is_changing = True
        while M_is_changing:
            M_is_changing = False
            for A, r_rules in self.grammar.nonterminal_rules.items():
                for p in r_rules:
                    old_nvals = self.M[A].nvals
                    B_p = Matrix.sparse(BOOL, self.max_indices, self.max_indices)
                    C_p = Matrix.sparse(BOOL, self.max_indices, self.max_indices)

                    for elem in self.M[p[0]]:
                        beta = self.get_element_of_V(elem[0]) + self.get_element_of_V(elem[1])
                        first_index = sum(
                            beta[p[2][j]] * ((self.graph.matrices_size + 1) ** j) for j in range(len(p[2])))
                        second_index = sum(
                            beta[p[3][j]] * ((self.graph.matrices_size + 1) ** j) for j in range(len(p[3])))
                        B_p[first_index, second_index] = True

                    for elem in self.M[p[1]]:
                        gamma = self.get_element_of_V(elem[0]) + self.get_element_of_V(elem[1])
                        second_index = sum(
                            gamma[p[4][j] - 2 * self.grammar.d_by_N[p[0]]] * ((self.graph.matrices_size + 1) ** j) for j
                            in range(len(p[4])))
                        first_index = sum(
                            gamma[p[5][j] - 2 * self.grammar.d_by_N[p[0]]] * ((self.graph.matrices_size + 1) ** j) for j
                            in range(len(p[5])))
                        C_p[first_index, second_index] = True

                    with BOOL.LOR_LAND:
                        A_p = B_p @ C_p

                    for elem in A_p:
                        i = self.get_element_of_V(elem[0])
                        j = self.get_element_of_V(elem[1])

                        indices = []
                        for end_l, end_r in p[6]:
                            if end_l < 2 * self.grammar.d_by_N[p[0]]:
                                indices.append(i[p[2].index(end_l)])
                            else:
                                indices.append(j[p[4].index(end_l)])

                            if end_r < 2 * self.grammar.d_by_N[p[0]]:
                                indices.append(i[p[2].index(end_r)])
                            else:
                                indices.append(j[p[4].index(end_r)])

                        left = indices[:len(indices) // 2]
                        right = indices[len(indices) // 2:]
                        first_index = sum(left[j] * ((self.graph.matrices_size + 1) ** j) for j in range(len(left)))
                        second_index = sum(right[j] * ((self.graph.matrices_size + 1) ** j) for j in range(len(right)))
                        self.M[A][first_index, second_index] = True

                    M_is_changing = M_is_changing or (True if old_nvals != self.M[A].nvals else False)
