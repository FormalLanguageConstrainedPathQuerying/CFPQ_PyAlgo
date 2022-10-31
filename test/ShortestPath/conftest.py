import pytest

from src.problems.SinglePath.algo.matrix_shortest_path.matrix_shortest_path_index import MatrixShortestAlgo


@pytest.fixture(params=[MatrixShortestAlgo])
def algo(request):
    return request.param