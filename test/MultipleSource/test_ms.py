import pytest
from cfpq_data import cfg_from_txt
from src.graph.graph import Graph

from src.problems.MultipleSource.MultipleSource import MultipleSourceProblem

from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.problems.utils import ResultAlgo


@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('binary_tree')
    ms_algo: MultipleSourceProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    ms_algo.prepare(graph, grammar)

    result: ResultAlgo
    result, with_cache = ms_algo.solve([0])
    assert result.matrix_S.nvals == 4 and with_cache.nvals == 6


@pytest.mark.CI
def test_line(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('line')
    ms_algo: MultipleSourceProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    ms_algo.prepare(graph, grammar)

    result: ResultAlgo
    result, with_cache = ms_algo.solve([1])
    assert result.matrix_S.nvals == 1 and with_cache.nvals == 1


@pytest.mark.CI
def test_two_nonterm(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('two_nonterm')
    ms_algo: MultipleSourceProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    ms_algo.prepare(graph, grammar)

    result: ResultAlgo
    result, with_cache = ms_algo.solve([1])
    assert result.matrix_S.nvals == 1 and with_cache.nvals == 1
