from tests.suites import ALL_TEST_CASES, get_markers


def pytest_configure(config):
    for suite, graph, grammar in ALL_TEST_CASES:
        for mark in get_markers(suite, graph, grammar):
            config.addinivalue_line(
                'markers', f'{mark}: generated marker'
            )
