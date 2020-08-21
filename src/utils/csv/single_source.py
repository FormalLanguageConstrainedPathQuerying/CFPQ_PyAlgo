import os

import pandas as pd

from src.utils.file_helpers import get_file_name


class TestSingleSourceBenchmarkGranularityWrapper:
    def __init__(self, timed_results_path):
        self.results_path = timed_results_path

    def load_csv(self, graph):
        df = pd.read_csv(os.path.join(self.results_path, graph))
        df['times'] = df['times'].apply(eval)
        return df


class TestSingleSourceBenchmarkTotal:
    def __init__(self, bench_csv_path):
        self.df = pd.read_csv(bench_csv_path)

    def group_by_graph_grammar_chunk(self):
        def parse_algo(algo):
            return algo.split('.')[-1].split("'")[0]

        # (graph, grammar, chunk) -> (algo_1_time, ..., algo_n_time)
        result = {}
        algos = set()
        for index, raw in self.df.iterrows():
            graph = get_file_name(raw['param:graph'])
            grammar = get_file_name(raw['param:grammar'])
            chunk = raw['param:chunk_size']
            if pd.isnull(chunk):
                chunk = 100000
            chunk = int(chunk)
            algo = parse_algo(raw['param:algo'])
            mean = raw['mean']
            stddev = raw['stddev']

            algos.add(algo)
            result.setdefault((graph, grammar, chunk), {})
            result[(graph, grammar, chunk)][algo] = (mean, stddev)

        result_csv = {
            'graph': [],
            'grammar': [],
            'chunk_size': [],
        }
        for algo in algos:
            result_csv[f'{algo}Time'] = []
        for algo in algos:
            result_csv[f'{algo}StdDev'] = []

        for graph, grammar, chunk in sorted(result):
            print(graph, grammar, chunk)
            result_csv['graph'].append(graph)
            result_csv['grammar'].append(grammar)
            result_csv['chunk_size'].append(chunk)
            for algo in algos:
                result_csv[f'{algo}Time'].append(result[(graph, grammar, chunk)][algo][0])
                result_csv[f'{algo}StdDev'].append(result[(graph, grammar, chunk)][algo][1])
        return pd.DataFrame(result_csv)


# Example of usage
wrapper = TestSingleSourceBenchmarkTotal('../../.benchmarks/Linux-CPython-3.8-64bit/0002_small-rdf-total.csv')
df = wrapper.group_by_graph_grammar_chunk()
df.to_csv('small_rdf_total_results.csv')

