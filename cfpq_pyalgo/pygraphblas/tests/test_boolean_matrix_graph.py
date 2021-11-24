import networkx as nx
import pytest
from pygraphblas import Matrix, BOOL

import cfpq_pyalgo.pygraphblas as algo


def test_empty():
    g = nx.MultiDiGraph()

    bmg, _ = algo.bmg_from_nx_graph(g)

    assert bmg._matrices_size == 0
    assert bmg._matrices == dict()


def test_one_edge():
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="label")

    bmg, _ = algo.bmg_from_nx_graph(g)

    assert bmg._matrices_size == 2
    assert bmg._matrices == {
        "label": Matrix.from_lists(
            I=[0],
            J=[1],
            V=[True],
            nrows=2,
            ncols=2,
            typ=BOOL,
        )
    }


def test_two_edges():
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="A")
    g.add_edge(1, 2, label="B")

    bmg, _ = algo.bmg_from_nx_graph(g)

    assert bmg._matrices_size == 3
    assert bmg._matrices == {
        "A": Matrix.from_lists(
            I=[0],
            J=[1],
            V=[True],
            nrows=3,
            ncols=3,
            typ=BOOL,
        ),
        "B": Matrix.from_lists(
            I=[1],
            J=[2],
            V=[True],
            nrows=3,
            ncols=3,
            typ=BOOL,
        ),
    }


def test_vertices_numbering():
    g = nx.MultiDiGraph()
    g.add_edge(5, 1, label="A")
    g.add_edge(1, 9, label="B")
    g.add_edge(9, 5, label="A")

    bmg, _ = algo.bmg_from_nx_graph(g)

    assert bmg._matrices_size == 3
    assert bmg._matrices == {
        "A": Matrix.from_lists(
            I=[0, 2],
            J=[1, 0],
            V=[True, True],
            nrows=3,
            ncols=3,
            typ=BOOL,
        ),
        "B": Matrix.from_lists(
            I=[1],
            J=[2],
            V=[True],
            nrows=3,
            ncols=3,
            typ=BOOL,
        ),
    }


def test_vertices_numbers_conversion():
    g = nx.MultiDiGraph()
    g.add_edge(5, 1, label="A")
    g.add_edge(1, 9, label="B")
    g.add_edge(9, 5, label="A")

    bmg, nodes_mapping = algo.bmg_from_nx_graph(g)

    assert set(nodes_mapping) == {1, 5, 9}


def test_key_error():
    g = nx.MultiDiGraph()

    bmg, _ = algo.bmg_from_nx_graph(g)

    with pytest.raises(KeyError):
        print(bmg["KeyError"])
