import pytest

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


def test_two_edges():
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="A")
    g.add_edge(1, 2, label="B")

    bmg = algo.BooleanMatrixGraph.from_nx_graph(g)

    assert bmg._matrices_size == 3
    assert bmg._matrices == {
        "A": Matrix.from_lists(
            I=[0],
            J=[1],
            nrows=3,
            ncols=3,
            typ=BOOL,
        ),
        "B": Matrix.from_lists(
            I=[1],
            J=[2],
            nrows=3,
            ncols=3,
            typ=BOOL,
        ),
    }


def test_KeyError():
    g = nx.MultiDiGraph()

    bmg = algo.BooleanMatrixGraph.from_nx_graph(g)

    with pytest.raises(KeyError):
        print(g["KeyError"])
