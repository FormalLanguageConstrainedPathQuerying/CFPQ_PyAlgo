from itertools import product
from typing import Dict

from pyformlang.finite_automaton.state import State
from pyformlang.finite_automaton import EpsilonNFA
from pyformlang.finite_automaton.symbol import Symbol

from pygraphblas.types import BOOL
from pygraphblas.matrix import Matrix
from pygraphblas.vector import Vector
from pygraphblas import semiring, descriptor

from src.graph.graph import Graph
from src.problems.MultipleSource.algo.matrix_bfs.reg_automaton import RegAutomaton


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
        graph_start_states = [0]  # should be an argument

        # initialize matrices for multiple source bfs
        found = Matrix.sparse(BOOL, len(regex_start_states), num_verts_diag)
        vect = Matrix.sparse(BOOL, len(regex_start_states), num_verts_diag)

        # fill start states
        for start_state in self.regular_automaton.start_states:
            found[
                start_state % len(regex_start_states),
                start_state,
            ] = True
        for start_state in graph_start_states:
            found[
                len(regex_start_states) - 1 + start_state,
                num_vert_regex + start_state,
            ] = True

        # initialize matrix which stores front nodes found on each iteration for every symbol
        iter_found = found.dup()

        not_empty = True
        level = 0

        while not_empty and level < num_verts_inter:
            # for each symbol we are going to store if any new nodes were found during traversal
            # if none are found, then 'not_empty' flag turns False, which means that no matrices change anymore
            # and we can stop the traversal
            not_empty_for_at_least_one_symbol = False

            vect.assign_scalar(True, mask=iter_found)

            for symbol in regex:
                if symbol in graph:
                    with semiring.ANY_PAIR_BOOL:
                        found = vect.mxm(
                            diag_matrices[symbol], mask=vect, desc=descriptor.RC
                        )

                    # append newly found nodes
                    iter_found.assign_scalar(True, mask=found, desc=descriptor.S)

                    # the problem now is that I'm not sure how to store bfs' front edges
                    # of intersection automata, since 'found' matrix doesn't store
                    # information about which pair of nodes is in front at the moment

                    # TODO: then here I should assign matrix elements to True

                    # check if new nodes were found. if positive, switch the flag
                    if found.reduce_bool():
                        not_empty_for_at_least_one_symbol = True

            not_empty = not_empty_for_at_least_one_symbol
            level += 1

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
