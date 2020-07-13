from pygraphblas import *

from src.graph.label_graph import LabelGraph
from src.grammar.rsa import RecursiveAutomaton


def tensor_algo(graph: LabelGraph, grammar: RecursiveAutomaton):
    for start in grammar.S():
        graph.matrices.update({start: Matrix.sparse(BOOL, graph.matrices_size, graph.matrices_size)})

    sizeKronecker = graph.matrices_size * grammar.matrices_size()

    kron = Matrix.sparse(BOOL, sizeKronecker, sizeKronecker)
    control_sum = 0
    changed = True
    while changed:
        changed = False

        # calculate kronecker
        for label in grammar.labels().union(grammar.S()):
            kron += grammar.automaton()[label].kron(graph[label])

        # transitive closer
        prev = 0
        degree = kron
        transitive_changed = True
        while transitive_changed:
            transitive_changed = False
            degree = degree @ kron
            degree.select(lib.GxB_NONZERO)
            kron += degree
            cur = kron.nvals
            if prev != cur:
                prev = cur
                transitive_changed = True


        # update
        for start in grammar.S():
            states = grammar.states()[start]
            for element in states:
                i = element[0]
                j = element[1]

                start_i = i * graph.matrices_size
                start_j = j * graph.matrices_size
                block = kron[start_i:start_i + graph.matrices_size - 1, start_j: start_j + graph.matrices_size - 1]

                with semiring.LOR_LAND_BOOL:
                    graph[start] += block
                new_control_sum = graph[start].nvals

                if new_control_sum != control_sum:
                    changed = True
                    control_sum = new_control_sum

    return control_sum
