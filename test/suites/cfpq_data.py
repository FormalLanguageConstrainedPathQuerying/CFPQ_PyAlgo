import pytest
from cfpq_data_devtools.data_wrapper import DataWrapper
from src.utils.file_helpers import get_file_name, get_file_size


def get_markers(suite, graph, grammar):
    return [suite, get_file_name(graph), get_file_name(grammar)]


def get_all_test_cases(cfpq_data_path):
    data = DataWrapper(cfpq_data_path)
    return [
        (suite, graph, grammar)
        for suite in data.get_suites()
        for graph in data.get_graphs(suite, include_extensions=['txt'])
        for grammar in data.get_grammars(suite, include_extension=['cnf'])
    ]


def get_all_test_cases_params(cfpq_data_path):
    return [
        pytest.param(graph, grammar,
                     marks=[getattr(pytest.mark, mark) for mark in get_markers(suite, graph, grammar)],
                     id=f'{get_file_name(graph)}-{get_file_name(grammar)}')
        for suite, graph, grammar in get_all_test_cases(cfpq_data_path)
    ]


def all_cfpq_data_test_cases(cfpq_data_path):
    def decorator(f):
        return pytest.mark.parametrize(
            'graph,grammar',
            get_all_test_cases_params(cfpq_data_path)
        )(f)
    return decorator
