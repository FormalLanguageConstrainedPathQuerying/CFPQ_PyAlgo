import pytest

from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSOptAlgo, MatrixMSBruteAlgo
from src.problems.MultipleSource.algo.tensor_ms.tensor_ms import TensorMSAlgo


@pytest.fixture(params=[MatrixMSOptAlgo, MatrixMSBruteAlgo, TensorMSAlgo])
def algo(request):
    return request.param
