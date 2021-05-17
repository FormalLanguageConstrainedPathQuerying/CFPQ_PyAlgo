import pytest

from src.problems.SinglePath.algo.matrix_single_path.matrix_single_path_index import MatrixSingleAlgo


@pytest.fixture(params=[MatrixSingleAlgo])
def algo(request):
    return request.param
