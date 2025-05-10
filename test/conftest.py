import os

from src.utils.useful_paths import LOCAL_CFPQ_DATA, POCR_FORMAT_DATA
from test.suites.cfpq_data import *


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'CI: small test to run in CI'
    )

    for suite, graph, grammar in get_all_test_cases(LOCAL_CFPQ_DATA):
        for mark in get_markers(suite, graph, grammar):
            config.addinivalue_line(
                'markers', f'{mark}: generated marker'
            )


@pytest.fixture(params=os.listdir(POCR_FORMAT_DATA))
def pocr_data_path(request):
    base_path: str = os.path.abspath(POCR_FORMAT_DATA)
    subfolder_path: str = os.path.join(base_path, request.param)
    if not os.path.isdir(subfolder_path):
        pytest.skip(f"{request.param} is not a directory")
        return None
    if not os.path.exists(os.path.join(subfolder_path, "expected_all_pairs_reachability.txt")):
        pytest.skip(f"{request.param} doesn't contain 'expected_all_pairs_reachability.txt'")
        return None
    return subfolder_path
