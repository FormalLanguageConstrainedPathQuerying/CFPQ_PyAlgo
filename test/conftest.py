from src.utils.useful_paths import GLOBAL_CFPQ_DATA, LOCAL_CFPQ_DATA
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
