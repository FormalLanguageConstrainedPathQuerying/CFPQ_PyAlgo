from pygraphblas import *

from src.graph.label_graph import LabelGraph
from src.grammar.rsa import RecursiveAutomaton


def tensor_algo(graph: LabelGraph, grammar: RecursiveAutomaton):
    for start in grammar.S():
        graph.matrices.update({start: Matrix.sparse(BOOL, graph.matrices_size, graph.matrices_size)})

    for label in grammar.start_and_finish():
        for i in range(graph.matrices_size):
            graph[label][i, i] = True

    sizeKron = graph.matrices_size * grammar.matrices_size()

    kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
    control_sum = 0
    count_tc = 0
    first_iter = True
    changed = True
    while changed:
        changed = False

        # calculate kronecker
        for label in grammar.labels():
            with semiring.LOR_LAND_BOOL:
                kron += grammar.automaton()[label].kron(graph[label])

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
        for start in grammar.S():
            for element in grammar.states()[start]:
                i = element[0]
                j = element[1]

                start_i = i * graph.matrices_size
                start_j = j * graph.matrices_size
                block = kron[start_i:start_i + graph.matrices_size - 1, start_j: start_j + graph.matrices_size - 1]
                block.select(lib.GxB_NONZERO)

                with semiring.LOR_LAND_BOOL:
                    graph[start] += block
                    graph[start].select(lib.GxB_NONZERO)
                new_control_sum = graph[start].nvals

                if new_control_sum != control_sum:
                    changed = True
                    control_sum = new_control_sum

    return control_sum, graph, kron, count_tc
