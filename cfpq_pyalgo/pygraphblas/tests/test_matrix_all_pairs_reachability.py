import cfpq_pyalgo.pygraphblas as algo

import networkx as nx
from pyformlang.cfg import CFG


def test_empty_graph():
    g = nx.MultiDiGraph()
    cfg = CFG.from_text("S -> a")

    reachable_vertices = algo.matrix_all_pairs_reachability(g, cfg)
    assert reachable_vertices == []


def test_no_reachable_vertices():
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="b")
    g.add_edge(1, 2, label="c")
    g.add_edge(2, 0, label="d")

    cfg = CFG.from_text("S -> S S | a")

    reachable_vertices = algo.matrix_all_pairs_reachability(g, cfg)
    assert reachable_vertices == []


def test_worst_case():
    # The graph is two cycles of coprime lengths with a single common vertex.
    # The first cycle is labeled by the open bracket and the second cycle is labeled by the close bracket
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="a")
    g.add_edge(2, 0, label="a")
    g.add_edge(0, 3, label="b")
    g.add_edge(3, 0, label="b")

    cfg = CFG.from_text("S -> a S b | a b")

    reachable_vertices = algo.matrix_all_pairs_reachability(g, cfg)

    assert set(reachable_vertices) == {(0, 0), (0, 3), (1, 0), (1, 3), (2, 0), (2, 3)}


def test_full_graph_result():
    # The case when the input graph is sparse, but the result is a full graph.
    # Input graph is a cycle, all edges of which are labeled by the same token
    g = nx.MultiDiGraph()
    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="a")
    g.add_edge(2, 3, label="a")
    g.add_edge(3, 0, label="a")

    cfg = CFG.from_text("S -> S S | a")

    reachable_vertices = algo.matrix_all_pairs_reachability(g, cfg)

    assert set(reachable_vertices) == set(
        [
            (v, to)
            for v in range(g.number_of_nodes())
            for to in range(g.number_of_nodes())
        ]
    )
