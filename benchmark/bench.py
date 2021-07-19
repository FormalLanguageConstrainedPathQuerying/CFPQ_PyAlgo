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


def get_sample_mean(data):
    return sum(data) / float(len(data))


def get_variance(data, sample_mean):
    return sum([(x - sample_mean) ** 2 for x in data]) / float(len(data) - 1)


def benchmark_all_pairs(graph, grammar, csv_writer, rounds):
    algo = MatrixBaseAlgo()
    algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))
    count_S = 0
    times = []
    for _ in tqdm(range(rounds), desc=f'{graph.stem}-{grammar.stem}'):
        algo.prepare_for_solve()
        start = time()
        res = algo.solve()
        finish = time()
        times.append(finish - start)
        count_S = res.matrix_S.nvals

    sample_mean = get_sample_mean(times)
    csv_writer.writerow(
        [grammar.stem, sample_mean, count_S, get_variance(times, sample_mean)])
    return res.matrix_S.dup()


def benchmark_ms_distribution(graph, grammar, csv_writer, algo_impl_name, reachable_restriction,
                              all_pairs_result):
    algo = algo_impl_name()
    algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))
    results = []
    for vertex in tqdm(range(all_pairs_result.nrows), desc=f'{graph.stem}-{grammar.stem}'):
        if all_pairs_result.extract_row(vertex).nvals >= reachable_restriction:
            algo.clear_src()
            start = time()
            res, _ = algo.solve([vertex])
            finish = time()
            work_time = finish - start
            csv_writer.writerow([vertex, work_time, res.matrix_S.nvals])
            results.append((vertex, work_time))
    return results


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


def get_all_pairs_csv_writer(graph, result_dir):
    all_pairs_header = ['grammar', 'time', 'count_S', 'variance']
    all_pairs_filename = f'{graph.stem}-All_pairs'
    return get_csv_writer(result_dir, all_pairs_filename, all_pairs_header)


def get_ms_distribution_csv_writer(graph, grammar, result_dir):
    all_pairs_header = ['vertex', 'time', 'count_S']
    all_pairs_filename = f'{graph.stem}-{grammar.stem}-Multiple_sources_distribution'
    return get_csv_writer(result_dir, all_pairs_filename, all_pairs_header)


def get_ms_worst_csv_writer(graph, grammar, result_dir):
    all_pairs_header = ['vertex', 'time', 'count_S']
    all_pairs_filename = f'{graph.stem}-{grammar.stem}-Multiple_sources_worst'
    return get_csv_writer(result_dir, all_pairs_filename, all_pairs_header)


def benchmark(all_pairs_rounds, ms_algo_name, reachable_restriction, ms_worst_rounds, worst_vertices_count, data_dir,
              result_dir):
    """
    Function for measuring performance for multiple sources problem
    @param all_pairs_rounds: number of measurement rounds for all pairs problem
    @param ms_algo_name: name multiple sources algorithm in string
    @param reachable_restriction: minimal number of reachable vertices to measure algo
    @param ms_worst_rounds: number of measurement rounds to measure worst case
    @param worst_vertices_count: number of vertices to measure worst case
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
            ms_distr_csv_writer = get_ms_distribution_csv_writer(graph, grammar, result_dir)
            ms_worst_csv_writer = get_ms_worst_csv_writer(graph, grammar, result_dir)

            all_pairs_result = benchmark_all_pairs(graph, grammar, all_pairs_csv_writer, all_pairs_rounds)
            ms_worst_results = benchmark_ms_distribution(graph, grammar, ms_distr_csv_writer, ms_algo,
                                                         reachable_restriction,
                                                         all_pairs_result)
            ms_worst_results = sorted(ms_worst_results, key=lambda vertex_time: vertex_time[1], reverse=True)
            ms_worst_results = map(lambda vertex_time: vertex_time[0], ms_worst_results[:worst_vertices_count])
            benchmark_ms_worst_result(graph, grammar, ms_worst_csv_writer, ms_algo, ms_worst_results, ms_worst_rounds)
