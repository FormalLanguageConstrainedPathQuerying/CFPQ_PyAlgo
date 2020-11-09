import pytest

from src.algo.tensor.tensor import tensor_algo
from src.grammar.rsa import RecursiveAutomaton
from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.graph.label_graph import LabelGraph


@pytest.mark.CI
def test_case_cycle():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_cycle')
    graph = LabelGraph.from_txt(path.joinpath('graph_cycle'))
    rsa = RecursiveAutomaton.from_file(path.joinpath('rsa_cycle'))
    control_sum, _, _, _ = tensor_algo(graph, rsa)
    assert control_sum == 9

@pytest.mark.CI
def test_case_loop():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_loop')
    graph = LabelGraph.from_txt(path.joinpath('graph_loop'))
    rsa = RecursiveAutomaton.from_file(path.joinpath('rsa_loop'))
    control_sum, _, _, _ = tensor_algo(graph, rsa)
    assert control_sum == 3

@pytest.mark.CI
def test_case_rpq():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_rpq')
    graph = LabelGraph.from_txt(path.joinpath('graph_rpq'))
    rsa = RecursiveAutomaton.from_file(path.joinpath('rsa_rpq'))
    control_sum, _, _, _ = tensor_algo(graph, rsa)
    assert control_sum == 5

@pytest.mark.CI
def test_case_simple():
    path = LOCAL_CFPQ_DATA.joinpath('tensor/test_simple')
    graph = LabelGraph.from_txt(path.joinpath('graph_simple'))
    rsa = RecursiveAutomaton.from_file(path.joinpath('rsa_simple'))
    control_sum, _, _, _ = tensor_algo(graph, rsa)
    assert control_sum == 2

test_case_loop()
test_case_rpq()
test_case_cycle()
test_case_simple()