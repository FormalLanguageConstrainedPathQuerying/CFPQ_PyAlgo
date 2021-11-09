import cfpq_pyalgo.pygraphblas as algo

import networkx as nx

from pygraphblas import Matrix, BOOL


def test_empty():
    g = nx.MultiDiGraph()

    bmg = algo.BooleanMatrixGraph.from_nx_graph(g)

    assert bmg._matrices_size == 0
    assert bmg._matrices == dict()


def test_one_edge():
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="label")

    bmg = algo.BooleanMatrixGraph.from_nx_graph(g)

    assert bmg._matrices_size == 2
    assert bmg._matrices == {
        "label": Matrix.from_lists(
            I=[0],
            J=[1],
            nrows=2,
            ncols=2,
            typ=BOOL,
        )
    }
