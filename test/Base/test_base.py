import pytest

from src.problems.Base.Base import BaseProblem

from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.problems.utils import ResultAlgo


@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('binary_tree')
    base_algo: BaseProblem = algo()
    base_algo.prepare(test_data_path.joinpath('Matrices/graph_1'), test_data_path.joinpath('Grammars/g'))

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 20


@pytest.mark.CI
def test_cycle(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('cycle')
    base_algo: BaseProblem = algo()
    base_algo.prepare(test_data_path.joinpath('Matrices/graph_1'), test_data_path.joinpath('Grammars/g'))

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 9


@pytest.mark.CI
def test_line(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('line')
    base_algo: BaseProblem = algo()
    base_algo.prepare(test_data_path.joinpath('Matrices/graph_1'), test_data_path.joinpath('Grammars/g'))

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 1


@pytest.mark.CI
def test_loop(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('loop')
    base_algo: BaseProblem = algo()
    base_algo.prepare(test_data_path.joinpath('Matrices/graph_1'), test_data_path.joinpath('Grammars/g'))

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 1


@pytest.mark.CI
def test_two_cycles(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('two_cycles')
    base_algo: BaseProblem = algo()
    base_algo.prepare(test_data_path.joinpath('Matrices/graph_1'), test_data_path.joinpath('Grammars/g'))

    result: ResultAlgo = base_algo.solve()
    assert result.matrix_S.nvals == 6
