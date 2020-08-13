import csv
import pytest
from tqdm import tqdm

from src.utils.file_helpers import get_file_name
from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.time_profiler import SimpleTimer
from src.algo.matrix_base import matrix_base_algo
from src.algo.single_source.single_source import SingleSourceAlgoBrute, SingleSourceAlgoSmart, SingleSourceAlgoOpt

from tests.suites import all_cfpq_data_test_cases


def print_vec(xs):
    for x in xs:
        print(x, end=' ')


@all_cfpq_data_test_cases
def test_correctness_per_vertex(graph, grammar, algo):
    CHUNK_COUNT = 20

    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    m = matrix_base_algo(g, gr)

    for chunk in tqdm(g.chunkify(max(g.matrices_size // CHUNK_COUNT, 1)), desc=graph):
        m1 = a.solve(chunk)
        assert m1.extract_matrix(chunk).iseq(m.extract_matrix(chunk))


@all_cfpq_data_test_cases
def test_correctness(graph, grammar, algo):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    m = matrix_base_algo(g, gr)
    m1 = a.solve(range(g.matrices_size))

    assert m.iseq(m1)


@all_cfpq_data_test_cases
@pytest.mark.parametrize('chunk_size', [None, *[2 ** i for i in range(7)]])
def test_algo(graph, grammar, algo, chunk_size):
    g = LabelGraph.from_txt(graph)
    g_name = get_file_name(graph)

    gr = CnfGrammar.from_cnf(grammar)
    gr_name = get_file_name(grammar)

    a = algo(g, gr)
    a_name = type(a).__name__

    chunks = g.chunkify(g.matrices_size if chunk_size is None else chunk_size)

    timer = SimpleTimer()

    csv_file = open('test_algo_results.csv', mode='a+', newline='\n')
    csv_writer = csv.writer(csv_file, delimiter=' ', quoting=csv.QUOTE_NONE, escapechar=' ')

    times_of_chunks = []

    for chunk in chunks:
        timer.tic()
        a.solve(chunk)
        chunk_time = timer.toc()

        times_of_chunks.append(chunk_time)

    csv_writer.writerow([g_name, gr_name, a_name, chunk_size, times_of_chunks])
