import pytest

from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo


@pytest.fixture(params=[MatrixBaseAlgo])
def algo(request):
    return request.param
