import pytest

from src.algo.tensor.tensor import TensorAlgoSimple, TensorAlgoDynamic
from src.utils.useful_paths import LOCAL_CFPQ_DATA


@pytest.mark.CI
def test_case_cycle():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_cycle')
    path_to_graph = path.joinpath('graph_cycle')
    path_to_grammar = path.joinpath('rsa_cycle')
    algo1 = TensorAlgoSimple(path_to_graph, path_to_grammar)
    algo2 = TensorAlgoDynamic(path_to_graph, path_to_grammar)

    res_graph1 = algo1.solve()
    res_graph2 = algo2.solve()
    assert res_graph1["S"].nvals == res_graph2["S"].nvals == 9


@pytest.mark.CI
def test_case_loop():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_loop')
    path_to_graph = path.joinpath('graph_loop')
    path_to_grammar = path.joinpath('rsa_loop')
    algo1 = TensorAlgoSimple(path_to_graph, path_to_grammar)
    algo2 = TensorAlgoDynamic(path_to_graph, path_to_grammar)

    res_graph1 = algo1.solve()
    res_graph2 = algo2.solve()
    assert res_graph1["S"].nvals == res_graph2["S"].nvals == 3


@pytest.mark.CI
def test_case_rpq():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_rpq')
    path_to_graph = path.joinpath('graph_rpq')
    path_to_grammar = path.joinpath('rsa_rpq')
    algo1 = TensorAlgoSimple(path_to_graph, path_to_grammar)
    algo2 = TensorAlgoDynamic(path_to_graph, path_to_grammar)

    res_graph1 = algo1.solve()
    res_graph2 = algo2.solve()
    assert res_graph1["S"].nvals == res_graph2["S"].nvals == 5


@pytest.mark.CI
def test_case_simple():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_simple')
    path_to_graph = path.joinpath('graph_simple')
    path_to_grammar = path.joinpath('rsa_simple')
    algo1 = TensorAlgoSimple(path_to_graph, path_to_grammar)
    algo2 = TensorAlgoDynamic(path_to_graph, path_to_grammar)

    res_graph1 = algo1.solve()
    res_graph2 = algo2.solve()
    assert res_graph1["S"].nvals == res_graph2["S"].nvals == 2
