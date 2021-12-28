from itertools import product
from typing import Dict

from pyformlang.finite_automaton.state import State
from pyformlang.finite_automaton import EpsilonNFA
from pyformlang.finite_automaton.symbol import Symbol

from pygraphblas.types import BOOL
from pygraphblas.matrix import Matrix
from pygraphblas.vector import Vector
from pygraphblas import semiring

from src.graph.graph import Graph
from src.problems.AllPaths.algo.matrix_bfs.reg_automaton import RegAutomaton


class Intersection:
    """
    Implementations of graph and regular grammar intersection algorithm
    """

    def __init__(self, graph: Graph, regular_automaton: RegAutomaton):
        self.graph = graph
        self.graph.load_bool_graph()
        self.regular_automaton = regular_automaton
        self.intersection_matrices = dict()
        self.__create_intersection_matrices__()

    def __create_intersection_matrices__(self):
        num_vert_graph = self.graph.get_number_of_vertices()
        num_vert_regex = self.regular_automaton.num_states
        num_verts_inter = num_vert_graph * num_vert_regex

        for symbol in self.regular_automaton.matrices:
            if symbol in self.graph:
                self.intersection_matrices[symbol] = Matrix.sparse(
                    BOOL, num_verts_inter, num_verts_inter
                )

    def __to_automaton__(self) -> EpsilonNFA:
        """
        Build automata from matrices
        """
        enfa = EpsilonNFA()
        graph_vertices_num = self.graph.get_number_of_vertices()

        start_states = [
            self.to_inter_coord(x, y)
            for x, y in product(
                range(graph_vertices_num), self.regular_automaton.start_states
            )
        ]

        final_states = [
            self.to_inter_coord(x, y)
            for x, y in product(
                range(graph_vertices_num), self.regular_automaton.final_states
            )
        ]

        for start_state in start_states:
            enfa.add_start_state(State(start_state))

        for final_state in final_states:
            enfa.add_final_state(State(final_state))

        for symbol in self.intersection_matrices:
            matrix = self.intersection_matrices[symbol]

            for row, col in zip(matrix.rows, matrix.cols):
                enfa.add_transition(State(row), Symbol(symbol), State(col))

        return enfa

    def to_inter_coord(self, graph_vert, reg_vert) -> int:
        """
        Converts coordinates of graph vertice and regex vertice
        to intersection coordinates vertice
        """
        return reg_vert * self.graph.get_number_of_vertices() + graph_vert

    def create_diag_matrices(self) -> Dict[str, Matrix]:
        """
        Create a block diagonal matrices from graph and regex matrices for each symbol
        """
        num_vert_graph = self.graph.get_number_of_vertices()
        num_vert_regex = self.regular_automaton.num_states
        diag_num_verts = num_vert_graph + num_vert_regex

        diag_matrices = dict()
        for symbol in self.regular_automaton.matrices:
            if symbol in self.graph:
                diag_matrix = Matrix.sparse(BOOL, diag_num_verts, diag_num_verts)
                diag_matrix.assign_matrix(
                    self.regular_automaton.matrices[symbol],
                    slice(0, num_vert_regex - 1),
                    slice(0, num_vert_regex - 1),
                )
                diag_matrix.assign_matrix(
                    self.graph[symbol],
                    slice(num_vert_regex, diag_num_verts - 1),
                    slice(num_vert_regex, diag_num_verts - 1),
                )

                diag_matrices[symbol] = diag_matrix

        return diag_matrices

    def intersect_bfs(self) -> EpsilonNFA:
        """
        Intersection implementation with synchronous breadth first traversal
        of a graph and regular grammar represented in automata
        """
        num_vert_graph = self.graph.get_number_of_vertices()
        num_vert_regex = self.regular_automaton.num_states

        num_verts_inter = num_vert_graph * num_vert_regex
        num_verts_diag = num_vert_graph + num_vert_regex

        graph = self.graph
        regex = self.regular_automaton.matrices

        regex_start_states = self.regular_automaton.start_states

        diag_matrices = self.create_diag_matrices()

        found = Vector.sparse(BOOL, num_verts_diag)
        vect = Vector.sparse(BOOL, num_verts_diag)

        # vectors of found nodes
        # should be done with mask probably, not a queue
        curr_front = list()
        visited = Vector.sparse(BOOL, num_verts_inter)

        for regex_start_st in regex_start_states:
            for gr_start_st in range(num_vert_regex, num_verts_diag):
                vect[regex_start_st] = True
                vect[gr_start_st] = True

                curr_front.append(vect)

                while len(curr_front) > 0:
                    vect = curr_front.pop(0)

                    for symbol in regex:
                        if symbol in graph:
                            with semiring.LOR_LAND_BOOL:
                                found = vect.vxm(diag_matrices[symbol])

                            reg_vert, grph_vert = tuple(vect.I)
                            prev_vert_index = self.to_inter_coord(
                                grph_vert - num_vert_regex, reg_vert
                            )
                            next_vert_index = prev_vert_index

                            visited[prev_vert_index] = True

                            if not found.iseq(vect) and len(list(found.I)) == 2:
                                reg_vert, grph_vert = tuple(found.I)

                                next_vert_index = self.to_inter_coord(
                                    grph_vert - num_vert_regex, reg_vert
                                )

                                if next_vert_index not in list(visited.I):
                                    curr_front.append(found)

                                matrix = self.intersection_matrices[symbol]
                                matrix[prev_vert_index, next_vert_index] = True

                vect.clear()

        return self.__to_automaton__()

    # For testing purposes
    def intersect_kron(self) -> EpsilonNFA:
        """
        Intersection implementation with kronecker product
        """
        regex = self.regular_automaton.matrices
        graph = self.graph

        for symbol in regex:
            if symbol in graph:
                self.intersection_matrices[symbol] = regex[symbol].kronecker(
                    graph[symbol]
                )

        return self.__to_automaton__()
