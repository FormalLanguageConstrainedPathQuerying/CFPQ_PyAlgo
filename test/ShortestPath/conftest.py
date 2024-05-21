import pytest


# If you use SuiteSparse:GraphBLAS 7, you can add `params=[MatrixShortestAlgo],
# but for this legacy implementation can't be used with SuiteSparse:GraphBLAS 8,
# which we now use by default.
@pytest.fixture(params=[])
def algo(request):
    return request.param