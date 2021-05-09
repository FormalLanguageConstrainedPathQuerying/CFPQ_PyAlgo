import pytest

from src.problems.MultipleSource.MultipleSource import MultipleSourceProblem

from src.utils.useful_paths import LOCAL_CFPQ_DATA
from src.problems.utils import ResultAlgo


@pytest.mark.CI
def test_binary_tree(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('binary_tree')
    ms_algo: MultipleSourceProblem = algo()
    ms_algo.prepare(test_data_path.joinpath('Matrices/graph_1'), test_data_path.joinpath('Grammars/g'))

    result: ResultAlgo = ms_algo.solve([0])
    assert result.matrix_S.nvals == 6


@pytest.mark.CI
def test_line(algo):
    test_data_path = LOCAL_CFPQ_DATA.joinpath('line')
    ms_algo: MultipleSourceProblem = algo()
    ms_algo.prepare(test_data_path.joinpath('Matrices/graph_1'), test_data_path.joinpath('Grammars/g'))

    result: ResultAlgo = ms_algo.solve([1])
    assert result.matrix_S.nvals == 1
