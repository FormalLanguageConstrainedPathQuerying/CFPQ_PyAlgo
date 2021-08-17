import pytest
from cfpq_data import cfg_from_txt
from src.graph.graph import Graph

from src.problems.AllPaths.AllPaths import AllPathsProblem

from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.problems.utils import ResultAlgo


@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('binary_tree')
    allpath_algo: AllPathsProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    allpath_algo.prepare(graph, grammar)

    result: ResultAlgo = allpath_algo.solve()
    assert result.matrix_S.nvals == 20

    allpath_algo.prepare_for_exctract_paths()
    paths = allpath_algo.getPaths(0, 3, "S", 5)
    assert len(paths) == 1


@pytest.mark.CI
def test_cycle(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('cycle')
    allpath_algo: AllPathsProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    allpath_algo.prepare(graph, grammar)

    result: ResultAlgo = allpath_algo.solve()
    print(result.matrix_S)
    assert result.matrix_S.nvals == 9

    allpath_algo.prepare_for_exctract_paths()
    paths = allpath_algo.getPaths(0, 1, "S", 3)
    assert len(paths) == 1


@pytest.mark.CI
def test_line(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('line')
    allpath_algo: AllPathsProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    allpath_algo.prepare(graph, grammar)

    result: ResultAlgo = allpath_algo.solve()
    assert result.matrix_S.nvals == 2

    allpath_algo.prepare_for_exctract_paths()
    paths = allpath_algo.getPaths(0, 4, "S", 2)
    assert len(paths) == 0


@pytest.mark.CI
def test_loop(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('loop')
    allpath_algo: AllPathsProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    allpath_algo.prepare(graph, grammar)

    result: ResultAlgo = allpath_algo.solve()
    assert result.matrix_S.nvals == 1

    allpath_algo.prepare_for_exctract_paths()
    paths = allpath_algo.getPaths(0, 0, "S", 1)
    assert len(paths) == 0


@pytest.mark.CI
def test_two_cycles(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('two_cycles')
    allpath_algo: AllPathsProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    allpath_algo.prepare(graph, grammar)

    result: ResultAlgo = allpath_algo.solve()
    assert result.matrix_S.nvals == 6

    allpath_algo.prepare_for_exctract_paths()
    paths = allpath_algo.getPaths(1, 3, "S", 3)
    assert len(paths) == 1


@pytest.mark.CI
def test_two_nonterm(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('two_nonterm')
    allpath_algo: AllPathsProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    allpath_algo.prepare(graph, grammar)

    result: ResultAlgo = allpath_algo.solve()
    assert result.matrix_S.nvals == 156

    allpath_algo.prepare_for_exctract_paths()
    paths = allpath_algo.getPaths(1, 1, "S", 3)
    assert len(paths) == 1
