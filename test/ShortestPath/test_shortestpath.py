import pytest
from cfpq_data import cfg_from_txt
from src.graph.graph import Graph

from src.problems.SinglePath.SinglePath import SinglePathProblem

from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.problems.utils import ResultAlgo

@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('single_vs_shortest')
    shortestpath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    shortestpath_algo.prepare(graph, grammar)

    result: ResultAlgo = shortestpath_algo.solve()
    assert result.matrix_S.nvals == 2

    length = shortestpath_algo.getPath(0, 7, "S")
    assert length == 6

@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('binary_tree')
    shortestpath_algo: SinglePathProblem = algo()
    graph = Graph.from_txt(test_data_path.joinpath('Graphs/graph_1.txt'))
    grammar = cfg_from_txt(test_data_path.joinpath('Grammars/g.cfg'))
    shortestpath_algo.prepare(graph, grammar)

    result: ResultAlgo = shortestpath_algo.solve()
    assert result.matrix_S.nvals == 20
