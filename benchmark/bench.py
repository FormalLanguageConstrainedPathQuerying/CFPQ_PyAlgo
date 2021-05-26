import csv
from os import listdir
from os.path import isfile, exists
from tqdm import tqdm
from time import time

from benchmark.algo_impl import ALGO_PROBLEM, ALGO_IMPL
from src.graph.label_graph import LabelGraph
from src.graph.graph import Graph
from cfpq_data import cfg_from_txt


GRAMMAR_DIR = 'Grammars/'
GRAPH_DIR = 'Graphs/'


def parse_config(config):
    """
    Returns information about which graph with which grammar to run
    @param config: Path to csv file with header:["Graph", "Grammar"]
    @return: dictionary in which keys are paths to graphs and values are paths to grammars
    """
    graph_grammar = dict()
    with open(config, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['graph'] in graph_grammar:
                graph_grammar[row['graph']].append(row['grammar'])
            else:
                graph_grammar[row['graph']] = [row['grammar']]
    return graph_grammar


def get_sample_mean(data):
    return sum(data) / float(len(data))


def get_variance(data, sample_mean):
    return sum([(x - sample_mean) ** 2 for x in data]) / float(len(data))


def benchmark(algo, data_dir, result_dir, config, with_paths, rounds):
    """
    Pipeline builder function for measuring performance
    @param algo: name algorithm in string
    @param data_dir: path to dataset
    @param result_dir: path to result directory
    @param config: path to config file (csv)
    @param with_paths: flag for setting measurements for fetching paths
    @param rounds: number of measurement rounds
    """
    type_problem = ALGO_PROBLEM[algo]
    graph_grammar = dict()
    if config is not None:
        name_graph_grammar = parse_config(config)
        for graph in name_graph_grammar:
            graph_grammar.update({data_dir.joinpath(GRAPH_DIR).joinpath(graph): []})
            for grammar in name_graph_grammar[graph]:
                graph_grammar[data_dir.joinpath(GRAPH_DIR).joinpath(graph)].append(
                    data_dir.joinpath(GRAMMAR_DIR).joinpath(grammar))
    else:
        grammars = {data_dir.joinpath(GRAMMAR_DIR).joinpath(f) for f in listdir(data_dir.joinpath(GRAMMAR_DIR)) if
                    isfile(data_dir.joinpath(GRAMMAR_DIR).joinpath(f))}
        graphs = {data_dir.joinpath(GRAPH_DIR).joinpath(f) for f in listdir(data_dir.joinpath(GRAPH_DIR)) if
                  isfile(data_dir.joinpath(GRAPH_DIR).joinpath(f))}
        for graph in graphs:
            graph_grammar.update({graph: grammars})

    impl_for_algo = ALGO_IMPL[algo]
    variances = []
    if type_problem == "MS":
        benchmark_ms(impl_for_algo, graph_grammar, result_dir)
    else:
        variances = benchmark_index(impl_for_algo, graph_grammar, result_dir, rounds)

    if with_paths:
        if type_problem == "AllPaths": benchmark_all_paths(impl_for_algo, graph_grammar, result_dir)
        if type_problem == "SinglePath": benchmark_single_path(impl_for_algo, graph_grammar, result_dir)


def benchmark_index(algo_name, data, result_dir, rounds):
    """
    Measurement function for finding paths between all pairs of vertices
    @param algo_name: concrete implementation of the algorithm
    @param data: dictionary in format {path to graph: list of paths to grammars}
    @param result_dir: directory for uploading results of measurement
    @param rounds: number of measurement rounds
    @return: variance value for each round of measurements
    """
    header_index = ['graph', 'grammar', 'time', 'count_S', 'variance']

    variances = []
    for graph in data:
        result_index_file_path = result_dir.joinpath(f'{graph.stem}-{algo_name.__name__}-index')

        append_header = False
        if not exists(result_index_file_path):
            append_header = True
        result_csv = open(result_index_file_path, mode='a', newline='\n')
        csv_writer_index = csv.writer(result_csv, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, escapechar=' ')

        if append_header:
            csv_writer_index.writerow(header_index)

        for grammar in data[graph]:
            algo = algo_name()
            algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))
            count_S = 0
            times = []
            for _ in tqdm(range(rounds), desc=f'{graph.stem}-{grammar.stem}'):
                start = time()
                res = algo.solve()
                finish = time()
                times.append(finish - start)
                count_S = res.matrix_S.nvals

            sample_mean = get_sample_mean(times)
            variances.append(get_variance(times, sample_mean))
            csv_writer_index.writerow([graph.stem, grammar.stem, sample_mean, count_S, get_variance(times, sample_mean)])

    return variances


def benchmark_all_paths(algo_name, data, result_dir):
    """
    Measurement function for extract all paths
    @param algo_name: concrete implementation of the algorithm
    @param data: dictionary in format {path to graph: list of paths to grammars}
    @param result_dir: directory for uploading results of measurement
    """
    header_paths = ['graph', 'grammar', 'count_paths', 'time']

    for graph in data:
        result_paths_file_path = result_dir.joinpath(f'{graph.stem}-{algo_name.__name__}-allpaths')

        append_header = False
        if not exists(result_paths_file_path):
            append_header = True

        result_csv = open(result_paths_file_path, mode='a', newline='\n')
        csv_writer_paths = csv.writer(result_csv, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, escapechar=' ')

        if append_header:
            csv_writer_paths.writerow(header_paths)

        for grammar in data[graph]:
            algo = algo_name()
            algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))
            res = algo_name.solve()
            for elem in tqdm(res.matrix_S, desc=f'{graph.stem}-{grammar.stem}-paths'):
                start = time()
                paths = algo.getPaths(elem[0], elem[1], "S")
                finish = time()
                csv_writer_paths.writerow([graph.stem, grammar.stem, len(paths), finish - start])


def benchmark_single_path(algo_name, data, result_dir):
    """
    Measurement function for extract single path
    @param algo_name: concrete implementation of the algorithm
    @param data: dictionary in format {path to graph: list of paths to grammars}
    @param result_dir: directory for uploading results of measurement
    """
    header_paths = ['graph', 'grammar', 'len_path', 'time']

    for graph in data:
        result_paths_file_path = result_dir.joinpath(f'{graph.stem}-{algo_name.__name__}-singlepaths')

        append_header = False
        if not exists(result_paths_file_path):
            append_header = True

        result_csv = open(result_paths_file_path, mode='a', newline='\n')
        csv_writer_paths = csv.writer(result_csv, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, escapechar=' ')

        if append_header:
            csv_writer_paths.writerow(header_paths)

        if not exists(result_paths_file_path):
            csv_writer_paths.writerow(header_paths)

        for grammar in data[graph]:
            algo = algo_name()
            algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))
            res = algo_name.solve()
            for elem in tqdm(res.matrix_S, desc=f'{graph.stem}-{grammar}-paths'):
                start = time()
                paths = algo.getPath(elem[0], elem[1], "S")
                finish = time()
                csv_writer_paths.writerow([graph.stem, grammar.stem, paths, finish - start])


def benchmark_ms(algo_name, data, result_dir):
    """
    Measurement function for finding paths from set of vertices
    @param algo_name: concrete implementation of the algorithm
    @param data: dictionary in format {path to graph: list of paths to grammars}
    @param result_dir: directory for uploading results of measurement
    """
    header_index = ['graph', 'grammar', 'size_chunk', 'time', 'count_S']

    chunk_sizes = [1, 2, 4, 8, 16, 32, 50, 100, 500, 1000, 5000, 10000, None]

    for graph in data:
        result_index_file_path = result_dir.joinpath(f'{graph.stem}-{algo_name.__name__}-msindex')

        append_header = False
        if not exists(result_index_file_path):
            append_header = True

        result_csv = open(result_index_file_path, mode='a', newline='\n')
        csv_writer_index = csv.writer(result_csv, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, escapechar=' ')

        if append_header:
            csv_writer_index.writerow(header_index)

        if not exists(result_index_file_path):
            csv_writer_index.writerow(header_index)

        g = LabelGraph.from_txt(graph)
        for grammar in data[graph]:
            algo = algo_name()
            algo.prepare(Graph.from_txt(graph), cfg_from_txt(grammar))

            for chunk_size in chunk_sizes:
                chunks = []
                if chunk_size is None:
                    chunks = g.chunkify(g.matrices_size)
                else:
                    chunks = g.chunkify(chunk_size)

                for chunk in tqdm(chunks, desc=f'{graph.stem}-{grammar.stem}'):
                    start = time()
                    res = algo.solve(chunk)
                    finish = time()

                    csv_writer_index.writerow(
                        [graph.stem, grammar.stem, chunk_size, finish - start, res.matrix_S.nvals])
