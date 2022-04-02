import pytest

from src.graph.graph import Graph

from src.problems.MultipleSource.algo.matrix_bfs.intersection import Intersection
from src.problems.MultipleSource.algo.matrix_bfs.reg_automaton import RegAutomaton

from src.utils.useful_paths import LOCAL_CFPQ_DATA


@pytest.mark.CI
def test_case_regular_cycle():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/cycle")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    
    source_verts = [0]
    result = intersection.intersect_bfs(source_verts)

    assert result.nvals == 2 * len(source_verts)


@pytest.mark.CI
def test_case_regular_disconnected():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/disconnected")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    
    source_verts = [0, 3]
    result = intersection.intersect_bfs(source_verts)

    assert result.nvals == 2 * len(source_verts)


@pytest.mark.CI
def test_case_regular_loop():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/loop")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    
    source_verts = [0, 2]
    result = intersection.intersect_bfs(source_verts)

    assert result.nvals == 0 * len(source_verts)


@pytest.mark.CI
def test_case_regular_midsymbol():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/midsymbol")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    
    source_verts = [0]
    result = intersection.intersect_bfs(source_verts)

    assert result.nvals == 1 * len(source_verts)


@pytest.mark.CI
def test_case_regular_two_cycles():
    test_data_path = LOCAL_CFPQ_DATA.joinpath("regular/two_cycles")

    graph = Graph.from_txt(test_data_path.joinpath("Graphs/graph_1.txt"))
    grammar = RegAutomaton.from_regex_txt(
        test_data_path.joinpath("Grammars/regex_1.txt")
    )

    intersection = Intersection(graph, grammar)
    
    source_verts = [0, 3]
    result = intersection.intersect_bfs(source_verts)

    assert result.nvals == 2 * len(source_verts)
