import cfpq_data
from itertools import islice

import networkx as nx
from pyformlang.cfg import CFG

from cfpq_pyalgo.pygraphblas import (
    TensorPathsExtractor,
)


def test_no_reachable_vertices():
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="b")
    g.add_edge(1, 2, label="c")
    g.add_edge(2, 0, label="d")

    cfg = CFG.from_text("S -> S S | a")

    graph_extractor = TensorPathsExtractor.build_path_extractor(g, cfg)

    assert list(graph_extractor.get_paths(0, 1, "S", 10)) == []
    assert list(graph_extractor.get_paths(1, 0, "S", 10)) == []
    assert list(graph_extractor.get_paths(1, 2, "S", 10)) == []
    assert list(graph_extractor.get_paths(2, 1, "S", 10)) == []
    assert list(graph_extractor.get_paths(0, 2, "S", 10)) == []
    assert list(graph_extractor.get_paths(2, 0, "S", 10)) == []


def test_binary_tree():
    g = nx.MultiDiGraph()
    g.add_edge(0, 2, label="a")
    g.add_edge(1, 2, label="a")
    g.add_edge(3, 5, label="a")
    g.add_edge(4, 5, label="a")
    g.add_edge(2, 6, label="a")
    g.add_edge(5, 6, label="a")
    g.add_edge(2, 0, label="b")
    g.add_edge(2, 1, label="b")
    g.add_edge(5, 3, label="b")
    g.add_edge(5, 4, label="b")
    g.add_edge(6, 2, label="b")
    g.add_edge(6, 5, label="b")

    cfg = CFG.from_text("S -> a S b | a b")

    graph_extractor = TensorPathsExtractor.build_path_extractor(g, cfg)

    assert list(graph_extractor.get_paths(0, 0, "S")) == [
        [(0, "a", 2), (2, "b", 0)],
        [(0, "a", 2), (2, "a", 6), (6, "b", 2), (2, "b", 0)],
    ]
    assert list(graph_extractor.get_paths(0, 1, "S")) == [
        [(0, "a", 2), (2, "b", 1)],
        [(0, "a", 2), (2, "a", 6), (6, "b", 2), (2, "b", 1)],
    ]
    assert list(graph_extractor.get_paths(0, 3, "S")) == [
        [(0, "a", 2), (2, "a", 6), (6, "b", 5), (5, "b", 3)],
    ]


def test_worst_case():
    # The graph is two cycles of coprime lengths with a single common vertex
    # The first cycle is labeled by the open bracket
    # The second cycle is labeled by the close bracket
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="a")
    g.add_edge(2, 0, label="a")
    g.add_edge(0, 3, label="b")
    g.add_edge(3, 0, label="b")

    cfg = CFG.from_text("S -> a S b | a b")

    graph_extractor: TensorPathsExtractor = TensorPathsExtractor.build_path_extractor(
        g, cfg
    )

    assert list(graph_extractor.get_paths(0, 1, "S", 14)) == []
    assert list(graph_extractor.get_paths(1, 2, "S", 14)) == []
    assert list(graph_extractor.get_paths(0, 2, "S", 14)) == []
    assert list(graph_extractor.get_paths(2, 3, "S", 6)) == [[(2, "a", 0), (0, "b", 3)]]
    assert list(graph_extractor.get_paths(0, 3, "S", 6)) == [
        [(0, "a", 1), (1, "a", 2), (2, "a", 0), (0, "b", 3), (3, "b", 0), (0, "b", 3)]
    ]
    assert sorted(list(graph_extractor.get_paths(2, 3, "S", 14))) == [
        [
            (2, "a", 0),
            (0, "a", 1),
            (1, "a", 2),
            (2, "a", 0),
            (0, "a", 1),
            (1, "a", 2),
            (2, "a", 0),
            (0, "b", 3),
            (3, "b", 0),
            (0, "b", 3),
            (3, "b", 0),
            (0, "b", 3),
            (3, "b", 0),
            (0, "b", 3),
        ],
        [(2, "a", 0), (0, "b", 3)],
    ]


def test_full_graph():
    # The case when the input graph is sparse, but the result is a full graph.
    # Input graph is a cycle, all edges of which are labeled by the same token
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="a")
    g.add_edge(2, 3, label="a")
    g.add_edge(3, 0, label="a")

    cfg = CFG.from_text("S -> S S | a")

    graph_extractor: TensorPathsExtractor = TensorPathsExtractor.build_path_extractor(
        g, cfg
    )

    assert list(islice(graph_extractor.get_paths(0, 1, "S", 1), 1)) == [[(0, "a", 1)]]
    assert list(islice(graph_extractor.get_paths(0, 2, "S", 2), 1)) == [
        [(0, "a", 1), (1, "a", 2)]
    ]
    assert list(islice(graph_extractor.get_paths(0, 3, "S", 3), 1)) == [
        [(0, "a", 1), (1, "a", 2), (2, "a", 3)]
    ]
    assert list(islice(graph_extractor.get_paths(0, 0, "S", 4), 1)) == [
        [(0, "a", 1), (1, "a", 2), (2, "a", 3), (3, "a", 0)]
    ]
    assert list(islice(graph_extractor.get_paths(0, 1, "S", 5), 2)) == [
        [(0, "a", 1)],
        [(0, "a", 1), (1, "a", 2), (2, "a", 3), (3, "a", 0), (0, "a", 1)],
    ]


def test_skos():
    # Test with graph from cfpq_data
    graph_path = cfpq_data.download("skos")
    g: nx.MultiDiGraph = cfpq_data.graph_from_csv(graph_path)

    cfg = CFG.from_text("S -> S subClassOf | subClassOf")
    graph_extractor: TensorPathsExtractor = TensorPathsExtractor.build_path_extractor(
        g, cfg
    )
    assert list(graph_extractor.get_paths(79, 35, "S")) == [[(79, "subClassOf", 35)]]
