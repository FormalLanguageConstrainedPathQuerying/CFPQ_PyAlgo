import pytest

from src.algo.matrix_single_path.matrix_single_path_index import MatrixSinglePathAlgo
from src.utils.useful_paths import LOCAL_CFPQ_DATA


@pytest.mark.CI
def test_case_1_graph_1():
    test_case_1_path = LOCAL_CFPQ_DATA.joinpath('test_case_1')

    path_to_graph = test_case_1_path.joinpath('Matrices/graph_1')
    path_to_grammar = test_case_1_path.joinpath('Grammars/grammar')
    algo = MatrixSinglePathAlgo(path_to_graph, path_to_grammar)

    res_graph = algo.solve()
    assert res_graph["S"].nvals == 2


@pytest.mark.CI
def test_case_1_graph_2():
    test_case_1_path = LOCAL_CFPQ_DATA.joinpath('test_case_1')

    path_to_graph = test_case_1_path.joinpath('Matrices/graph_2')
    path_to_grammar = test_case_1_path.joinpath('Grammars/grammar')
    algo = MatrixSinglePathAlgo(path_to_graph, path_to_grammar)

    res_graph = algo.solve()
    assert res_graph["S"].nvals == 20
