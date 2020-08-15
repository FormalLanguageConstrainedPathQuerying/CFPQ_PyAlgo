import pytest
from tqdm import tqdm

from src.algo.matrix_base import matrix_base_algo
from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.file_helpers import get_file_name
from src.utils.useful_paths import GLOBAL_CFPQ_DATA, LOCAL_CFPQ_DATA
from test.suites.cfpq_data import all_cfpq_data_test_cases


def check_single_source_per_chunk(graph, grammar, algo, chunk_count=None, verbose=True):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    m = matrix_base_algo(g, gr)

    if chunk_count is None:
        chunk_count = g.matrices_size
    chunk_size = max(g.matrices_size // chunk_count, 1)
    chunks = g.chunkify(chunk_size)
    for chunk in tqdm(chunks, desc=get_file_name(graph)) if verbose else chunks:
        m1, _ = a.solve(chunk)
        assert m1.extract_matrix(chunk).iseq(m.extract_matrix(chunk))


@pytest.mark.parametrize('chunk_count', [1, 20])
@all_cfpq_data_test_cases(GLOBAL_CFPQ_DATA)
def test_correctness_per_chunk(graph, grammar, algo, chunk_count):
    check_single_source_per_chunk(graph, grammar, algo, chunk_count)


@pytest.mark.CI
@all_cfpq_data_test_cases(LOCAL_CFPQ_DATA)
def test_correctness_per_chunk_small_data(graph, grammar, algo):
    check_single_source_per_chunk(graph, grammar, algo, verbose=False)
