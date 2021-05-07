import pytest

from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSOptAlgo, MatrixMSBruteAlgo, MatrixMSSmartAlgo


@pytest.fixture(params=[MatrixMSOptAlgo, MatrixMSBruteAlgo, MatrixMSSmartAlgo])
def algo(request):
    return request.param
