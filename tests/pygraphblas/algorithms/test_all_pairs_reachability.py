import networkx as nx
import pytest

import cfpq_pyalgo


@pytest.mark.parametrize(
    "number_of_edges, grammar, expected_pairs",
    [
        (1, "S -> S S | a", [(0, 1)]),
        (2, "S -> S S | a", [(0, 1), (0, 2), (1, 2)]),
    ],
)
def test_path_graph(number_of_edges, grammar, expected_pairs):
    g = nx.MultiDiGraph()
    for i in range(number_of_edges):
        g.add_edge(i, i + 1, label="a")

    bmg = cfpq_pyalgo.pygraphblas.BooleanMatrixGraph.from_multidigraph(g)
    cnf = cfpq_pyalgo.classes.CNF.from_text(grammar)

    I, J, V = (
        cfpq_pyalgo.pygraphblas.all_pairs_reachability_matrix(bmg, cnf)
        .nonzero()
        .to_lists()
    )

    actual_pairs = list(zip(I, J))

    assert sorted(expected_pairs) == sorted(actual_pairs)
