import csv
import os

import pytest
from tqdm import tqdm

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.file_helpers import get_file_name
from src.utils.time_profiler import SimpleTimer
from tests.suites import all_cfpq_data_test_cases


@pytest.mark.parametrize('chunk_size', [1, 2, 4, 8, 16, 32, 50, 100, 500, 1000, 5000, 10000, None])
@all_cfpq_data_test_cases
def test_single_source_benchmark_total(graph, grammar, algo, chunk_size, benchmark):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    chunks = g.chunkify(g.matrices_size if chunk_size is None else chunk_size)

    if chunk_size is not None and chunk_size > g.matrices_size:
        return

    def run_suite():
        a = algo(g, gr)
        for chunk in tqdm(chunks, desc=f'{get_file_name(graph)}-{get_file_name(grammar)}-{algo.__name__}-{chunk_size}'):
            a.solve(chunk)

    benchmark.pedantic(run_suite, rounds=5, iterations=1, warmup_rounds=0)


@all_cfpq_data_test_cases
@pytest.mark.parametrize('chunk_size', [1, 2, 4, 8, 16, 32, 50, 100, 500, 1000, 5000, 10000, None])
def test_single_source_benchmark_granularity(graph, grammar, algo, chunk_size, result_folder):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    gr_name = get_file_name(grammar)
    a_name = type(a).__name__

    if chunk_size is None:
        chunk_size = g.matrices_size
    chunks = g.chunkify(chunk_size)

    result_file = f'{get_file_name(graph)}.csv'
    result_file_path = os.path.join(result_folder, result_file)
    append_headers = False
    if not os.path.exists(result_file_path):
        append_headers = True

    with open(result_file_path, mode='a', newline='\n') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, escapechar=' ')
        headers = ['grammar', 'algo', 'chunk_size', 'times']

        timer = SimpleTimer()
        times_of_chunks = []
        for chunk in chunks:
            timer.tic()
            a.solve(chunk)
            chunk_time = timer.toc()
            times_of_chunks.append(chunk_time)
        if append_headers:
            csv_writer.writerow(headers)
        csv_writer.writerow([gr_name, a_name, chunk_size, times_of_chunks])
