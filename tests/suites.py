import pytest
from pathlib import Path
from cfpq_data_devtools.data_wrapper import DataWrapper
from src.utils.file_helpers import get_file_name, get_file_size

CFPQ_DATA_PATH = Path(__file__).parent.parent.joinpath(Path('deps/CFPQ_Data/data')).absolute()
CFPQ_DATA = DataWrapper(CFPQ_DATA_PATH)


def get_markers(suite, graph, grammar):
    return [suite, get_file_name(graph), get_file_name(grammar)]


ALL_TEST_CASES = [
    (suite, graph, grammar)
    for suite in CFPQ_DATA.get_suites()
    for graph in CFPQ_DATA.get_graphs(suite, include_extensions=['txt'])
    for grammar in CFPQ_DATA.get_grammars(suite, include_extension=['cnf'])
]

ALL_TEST_CASES_PARAMS = [
    pytest.param(graph, grammar,
                 marks=[getattr(pytest.mark, mark) for mark in get_markers(suite, graph, grammar)],
                 id=f'{get_file_name(graph)}-{get_file_name(grammar)}')
    for suite, graph, grammar in ALL_TEST_CASES
]


def all_cfpq_data_test_cases(f):
    return pytest.mark.parametrize(
        'graph,grammar',
        ALL_TEST_CASES_PARAMS
    )(f)
