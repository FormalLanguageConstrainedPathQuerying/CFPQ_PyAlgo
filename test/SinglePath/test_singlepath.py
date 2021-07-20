import pytest
from cfpq_data import cfg_from_txt
from src.graph.graph import Graph

from src.problems.SinglePath.SinglePath import SinglePathProblem

from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.problems.utils import ResultAlgo


@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('binary_tree')
    singlepath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    singlepath_algo.prepare(graph, grammar)

    result: ResultAlgo = singlepath_algo.solve()
    assert result.matrix_S.nvals == 20

    paths = singlepath_algo.getPath(0, 3, "S")
    assert paths == 4


@pytest.mark.CI
def test_cycle(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('cycle')
    singlepath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    singlepath_algo.prepare(graph, grammar)

    result: ResultAlgo = singlepath_algo.solve()
    assert result.matrix_S.nvals == 9

    paths = singlepath_algo.getPath(0, 1, "S")
    assert paths == 1


@pytest.mark.CI
def test_line(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('line')
    singlepath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    singlepath_algo.prepare(graph, grammar)

    result: ResultAlgo = singlepath_algo.solve()
    assert result.matrix_S.nvals == 2

    paths = singlepath_algo.getPath(0, 4, "S")
    assert paths == 4


@pytest.mark.CI
def test_loop(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('loop')
    singlepath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    singlepath_algo.prepare(graph, grammar)

    result: ResultAlgo = singlepath_algo.solve()
    assert result.matrix_S.nvals == 1

    paths = singlepath_algo.getPath(0, 0, "S")
    assert paths == 1


@pytest.mark.CI
def test_two_cycles(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('two_cycles')
    singlepath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    singlepath_algo.prepare(graph, grammar)

    result: ResultAlgo = singlepath_algo.solve()
    assert result.matrix_S.nvals == 6

    paths = singlepath_algo.getPath(1, 3, "S")
    assert paths == 2


@pytest.mark.CI
def test_two_nonterm(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('two_nonterm')
    singlepath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    singlepath_algo.prepare(graph, grammar)

    result: ResultAlgo = singlepath_algo.solve()
    assert result.matrix_S.nvals == 156

    paths = singlepath_algo.getPath(1, 1, "S")
    assert paths == 2
