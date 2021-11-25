import cfpq_data
import networkx as nx
import pytest
from pyformlang.cfg import CFG

import cfpq_pyalgo.pygraphblas as algo


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

    reachable_vertices = algo.matrix_all_pairs_reachability(g, cfg)

    assert set(reachable_vertices) == {(0, 0), (1, 0), (0, 3), (1, 3), (2, 0), (2, 3)}


def test_worst_case_with_graph_vertices_numbering():
    # The graph is two cycles of coprime lengths with a single common vertex
    # The first cycle is labeled by the open bracket
    # The second cycle is labeled by the close bracket
    g = nx.MultiDiGraph()
    g.add_edge(-1, 7, label="a")
    g.add_edge(7, 2, label="a")
    g.add_edge(2, -1, label="a")
    g.add_edge(-1, "A", label="b")
    g.add_edge("A", -1, label="b")

    cfg = CFG.from_text("S -> a S b | a b")

    reachable_vertices = algo.matrix_all_pairs_reachability(g, cfg)

    assert set(reachable_vertices) == {
        (-1, -1),
        (7, -1),
        (-1, "A"),
        (2, -1),
        (7, "A"),
        (2, "A"),
    }


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

    assert set(reachable_vertices) == {
        (v, to) for v in range(g.number_of_nodes()) for to in range(g.number_of_nodes())
    }


@pytest.mark.parametrize(
    "graph_name, pairs",
    [
        ("skos", 30),
        ("generations", 12),
        ("travel", 52),
        ("univ", 25),
        ("atom", 6),
        ("biomedical", 47),
        ("foaf", 36),
        ("people", 51),
        ("funding", 58),
        ("wine", 565),
        ("pizza", 1356),
        ("core", 204),
        ("pathways", 884),
        ("enzyme", 396),
        ("eclass", 90994),
    ],
)
def test_dataset(graph_name, pairs):
    g1 = CFG.from_text(
        """
        S -> subClassOf_r S subClassOf | subClassOf_r subClassOf
        S -> type_r S type | type_r type
        """
    )

    path = cfpq_data.download(graph_name)
    graph = cfpq_data.graph_from_csv(path)

    reversed_edges = [
        (v, u, {"label": edge_data["label"] + "_r"})
        for u, v, edge_data in graph.edges(data=True)
    ]
    graph.add_edges_from(reversed_edges)

    res = algo.matrix_all_pairs_reachability(graph, g1)

    assert len(res) == pairs
