import pytest
from pathlib import Path
from cfpq_data_devtools.data_wrapper import DataWrapper
from src.utils.file_helpers import get_file_name, get_file_size

CFPQ_DATA_PATH = Path(__file__).parent.parent.joinpath(Path('deps/CFPQ_Data/data')).absolute()
CFPQ_DATA = DataWrapper(CFPQ_DATA_PATH)


ALL_TEST_CASES = [
    (suite, graph, grammar)
    for suite in CFPQ_DATA.get_suites()
    for graph in CFPQ_DATA.get_graphs(suite, include_extensions=['txt'])
    for grammar in CFPQ_DATA.get_grammars(suite, include_extension=['cnf'])
]

ALL_TEST_CASES_PARAMS = [
    pytest.param(graph, grammar,
                 marks=[
                     getattr(pytest.mark, suite),
                     getattr(pytest.mark, get_file_name(graph)),
                     getattr(pytest.mark, get_file_name(grammar)),
                     getattr(pytest.mark, 'small' if get_file_size(graph) <= 1000 else 'big')
                 ],
                 id=f'{get_file_name(graph)}-{get_file_name(grammar)}')
    for suite, graph, grammar in ALL_TEST_CASES
]


def graph_grammar_decorator(f):
    return pytest.mark.parametrize(
        'graph,grammar',
        ALL_TEST_CASES_PARAMS
    )(f)