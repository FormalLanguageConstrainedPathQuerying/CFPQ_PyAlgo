import pytest
from cfpq_data import cfg_from_txt
from src.graph.graph import Graph

from src.problems.Base.Base import BaseProblem

from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.problems.utils import ResultAlgo


@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('binary_tree')
    base_algo: BaseProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    base_algo.prepare(graph, grammar)

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 20


@pytest.mark.CI
def test_cycle(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('cycle')
    base_algo: BaseProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    base_algo.prepare(graph, grammar)

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 9


@pytest.mark.CI
def test_line(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('line')
    base_algo: BaseProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    base_algo.prepare(graph, grammar)

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 2


@pytest.mark.CI
def test_loop(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('loop')
    base_algo: BaseProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    base_algo.prepare(graph, grammar)

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 1


@pytest.mark.CI
def test_two_cycles(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('two_cycles')
    base_algo: BaseProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    base_algo.prepare(graph, grammar)

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 6
