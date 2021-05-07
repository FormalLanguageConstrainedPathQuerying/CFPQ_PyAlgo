import pytest

from src.problems.AllPaths.algo.tensor.tensor import TensorSimpleAlgo, TensorDynamicAlgo


@pytest.fixture(params=[TensorSimpleAlgo, TensorDynamicAlgo])
def algo(request):
    return request.param
