import csv
from os import listdir
from os.path import isfile, exists
from tqdm import tqdm
from time import time

from benchmark.algo_impl import ALGO_IMPL
from src.graph.graph import Graph
from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo
from cfpq_data import cfg_from_txt

GRAMMAR_DIR = 'Grammars/'
GRAPH_DIR = 'Graphs/'
CHUNK_DIR_TEMPLATE = 'Chunk_'


def get_sample_mean(data):
    return sum(data) / float(len(data))


def get_variance(data, sample_mean):
    return sum([(x - sample_mean) ** 2 for x in data]) / float(len(data) - 1)


def get_all_pairs_csv_writer(graph, result_dir):
    header = ['grammar', 'time', 'count_S', 'variance']
    filename = f'{graph.stem}-All_pairs'
    return get_csv_writer(result_dir, filename, header)


def get_ms_distribution_csv_writer(graph, grammar, result_dir):
    header = ['vertex', 'time', 'count_S']
    filename = f'{graph.stem}-{grammar.stem}-Multiple_sources_distribution'
    return get_csv_writer(result_dir, filename, header)


def get_ms_chunk_distribution_csv_writer(graph, grammar, chunk_size, result_dir):
    header = ['chunk_index', 'time', 'count_S']
    filename = f'{graph.stem}-{grammar.stem}--chunk_{chunk_size}-Multiple_sources_distribution'
    return get_csv_writer(result_dir, filename, header)


def get_ms_worst_csv_writer(graph, grammar, result_dir):
    header = ['vertex', 'time', 'count_S']
    filename = f'{graph.stem}-{grammar.stem}-Multiple_sources_worst'
    return get_csv_writer(result_dir, filename, header)


def benchmark_all_pairs(graph_path, grammar_path, csv_writer, rounds):
    if rounds == 0:
        return
    cfg = cfg_from_txt(grammar_path)
    graph = Graph.from_txt(graph_path)
    algo = MatrixBaseAlgo()
    algo.prepare(graph, cfg)
    count_S = 0
    times = []
    for _ in tqdm(range(rounds), desc=f'{graph_path.stem}-{grammar_path.stem}'):
        algo.prepare_for_solve()
        start = time()
        res = algo.solve()
        finish = time()
        times.append(finish - start)
        count_S = res.matrix_S.nvals

    sample_mean = get_sample_mean(times)
    csv_writer.writerow(
        [grammar_path.stem, sample_mean, count_S, get_variance(times, sample_mean)])


def benchmark_ms_distribution(graph, grammar, algo_impl_name, ms_chunks, data_dir, result_dir):
    algo = algo_impl_name()
    algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))
    results = []
    if ms_chunks:
        for chunk_size in ms_chunks:
            csv_writer = get_ms_chunk_distribution_csv_writer(graph, grammar, chunk_size, result_dir)
            path_to_chunks = data_dir.joinpath(f'{CHUNK_DIR_TEMPLATE}{chunk_size}/').joinpath(
                f'{graph.stem}_vertices.txt')
            with open(path_to_chunks) as chunks_f:
                for chunk_index in tqdm(range(int(chunks_f.readline())),
                                         desc=f'{graph.stem}-{grammar.stem}--chunk_{chunk_size}'):
                    chunk = list(map(int, chunks_f.readline().split(' ')))
                    algo.clear_src()
                    start = time()
                    res, _ = algo.solve(chunk)
                    finish = time()
                    work_time = finish - start
                    csv_writer.writerow([chunk_index, work_time, res.matrix_S.nvals])
        return

    csv_writer = get_ms_distribution_csv_writer(graph, grammar, result_dir)
    for vertex in tqdm(range(algo.graph.get_number_of_vertices()), desc=f'{graph.stem}-{grammar.stem}'):
        algo.clear_src()
        start = time()
        res, _ = algo.solve([vertex])
        finish = time()
        work_time = finish - start
        csv_writer.writerow([vertex, work_time, res.matrix_S.nvals])
        results.append((vertex, work_time))


def benchmark_ms_worst_result(graph, grammar, csv_writer, algo_impl_name, vertices, rounds):
    algo = algo_impl_name()
    algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))
    for vertex in tqdm(vertices, desc=f'{graph.stem}-{grammar.stem}'):
        for iteration in range(rounds):
            algo.clear_src()
            start = time()
            res, _ = algo.solve([vertex])
            finish = time()
            work_time = finish - start
            csv_writer.writerow([vertex, work_time, res.matrix_S.nvals])


def get_csv_writer(result_dir, filename, header):
    result_file_path = result_dir.joinpath(filename)
    append_header = False
    if not exists(result_file_path):
        append_header = True
    result_csv = open(result_file_path, mode='a', newline='\n')
    csv_writer = csv.writer(result_csv, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, escapechar=' ')
    if append_header:
        csv_writer.writerow(header)
    return csv_writer


def benchmark(all_pairs_rounds, ms_algo_name, ms_chunks, data_dir, result_dir):
    """
    Function for measuring performance for multiple sources problem
    @param all_pairs_rounds: number of measurement rounds for all pairs problem
    @param ms_algo_name: name multiple sources algorithm in string
    @param data_dir: path to dataset
    @param result_dir: path to result directory
    """
    graph_grammar = dict()
    grammars = {data_dir.joinpath(GRAMMAR_DIR).joinpath(f) for f in listdir(data_dir.joinpath(GRAMMAR_DIR)) if
                isfile(data_dir.joinpath(GRAMMAR_DIR).joinpath(f))}
    graphs = {data_dir.joinpath(GRAPH_DIR).joinpath(f) for f in listdir(data_dir.joinpath(GRAPH_DIR)) if
              isfile(data_dir.joinpath(GRAPH_DIR).joinpath(f))}
    for graph in graphs:
        graph_grammar.update({graph: grammars})

    ms_algo = ALGO_IMPL[ms_algo_name]
    for graph in graph_grammar:
        all_pairs_csv_writer = get_all_pairs_csv_writer(graph, result_dir)
        for grammar in graph_grammar[graph]:
            benchmark_all_pairs(graph, grammar, all_pairs_csv_writer, all_pairs_rounds)
            benchmark_ms_distribution(graph, grammar, ms_algo, ms_chunks, data_dir, result_dir)
