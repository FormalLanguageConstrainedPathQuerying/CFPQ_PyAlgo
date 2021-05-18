import pytest

from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSOptAlgo, MatrixMSBruteAlgo, MatrixMSSmartAlgo
from src.problems.MultipleSource.algo.tensor_ms.tensor_ms import TensorMSAlgo


@pytest.fixture(params=[MatrixMSOptAlgo, MatrixMSBruteAlgo, MatrixMSSmartAlgo, TensorMSAlgo])
def algo(request):
    return request.param
