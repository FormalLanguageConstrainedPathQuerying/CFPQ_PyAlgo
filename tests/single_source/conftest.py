import pytest

from src.algo.single_source.single_source import *


@pytest.fixture(params=[SingleSourceAlgoBrute, SingleSourceAlgoSmart, SingleSourceAlgoOpt])
def algo(request):
    return request.param
