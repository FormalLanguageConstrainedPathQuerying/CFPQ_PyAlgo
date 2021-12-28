import pytest

from src.graph.graph import Graph

from src.problems.AllPaths.algo.matrix_bfs.intersection import Intersection
from src.problems.AllPaths.algo.matrix_bfs.reg_automaton import RegAutomaton

from src.utils.useful_paths import LOCAL_CFPQ_DATA


@pytest.mark.CI
def test_case_regular_cycle():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/cycle")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    intersect_kron = intersection.intersect_kron()
    intersect_bfs = intersection.intersect_bfs()

    assert intersect_bfs.accepts(["a", "a"])
    assert intersect_bfs.accepts(["a", "a", "a"])

    assert not intersect_bfs.accepts(["a", "b"])
    assert not intersect_bfs.accepts(["b"])

    assert intersect_kron.is_equivalent_to(intersect_bfs)


@pytest.mark.CI
def test_case_regular_disconnected():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/disconnected")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    intersect_kron = intersection.intersect_kron()
    intersect_bfs = intersection.intersect_bfs()

    assert intersect_bfs.accepts(["a", "b"])
    assert intersect_bfs.accepts(["b", "a"])
    assert intersect_bfs.accepts(["a", "a", "b"])
    assert intersect_bfs.accepts(["a", "b", "a"])
    assert intersect_bfs.accepts(["b", "a", "b"])

    assert not intersect_bfs.accepts(["a"])
    assert not intersect_bfs.accepts(["c"])
    assert not intersect_bfs.accepts(["c", "b"])
    assert not intersect_bfs.accepts(["c", "a"])

    assert intersect_kron.is_equivalent_to(intersect_bfs)


@pytest.mark.CI
def test_case_regular_loop():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/loop")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    intersect_kron = intersection.intersect_kron()
    intersect_bfs = intersection.intersect_bfs()

    assert intersect_bfs.accepts(["a"])
    assert intersect_bfs.accepts(["a" for _ in range(10)])

    assert not intersect_bfs.accepts(["b"])
    assert not intersect_bfs.accepts(["c"])
    assert not intersect_bfs.accepts(["epsilon"])

    assert intersect_kron.is_equivalent_to(intersect_bfs)


@pytest.mark.CI
def test_case_regular_midsymbol():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/midsymbol")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    intersect_kron = intersection.intersect_kron()
    intersect_bfs = intersection.intersect_bfs()

    assert intersect_bfs.accepts(["b"])
    assert intersect_bfs.accepts(["a", "b", "c"])
    assert intersect_bfs.accepts(["a", "a", "b", "c", "c"])

    assert not intersect_bfs.accepts(["a"])
    assert not intersect_bfs.accepts(["c"])
    assert not intersect_bfs.accepts(["b", "b"])

    assert intersect_kron.is_equivalent_to(intersect_bfs)


@pytest.mark.CI
def test_case_regular_two_cycles():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/two_cycles")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    intersect_kron = intersection.intersect_kron()
    intersect_bfs = intersection.intersect_bfs()

    assert intersect_bfs.accepts(["a"])
    assert intersect_bfs.accepts(["a", "a"])

    assert not intersect_bfs.accepts(["b"])
    assert not intersect_bfs.accepts(["c"])

    assert intersect_kron.is_equivalent_to(intersect_bfs)
