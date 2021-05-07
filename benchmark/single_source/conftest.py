# Old
import datetime
import os

import pytest

from src.algo.single_source.single_source import *


@pytest.fixture(scope='session')
def result_folder():
    results = 'results'
    if not os.path.exists(results):
        os.mkdir(f'results')

    now = datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')
    result_folder = os.path.join(results, now)

    os.mkdir(result_folder)
    return result_folder


@pytest.fixture(params=[SingleSourceAlgoBrute, SingleSourceAlgoSmart, SingleSourceAlgoOpt])
def algo(request):
    return request.param
