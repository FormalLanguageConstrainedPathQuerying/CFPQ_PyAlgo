import argparse
from pathlib import Path, PosixPath
import os
import datetime

import algo_impl
from benchmark.bench import benchmark


def result_folder():
    results = 'results'
    if not os.path.exists(results):
        os.mkdir(f'results')

    now = datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')
    result_folder = os.path.join(results, now)

    os.mkdir(result_folder)
    return result_folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark implementations CFPQ's algorithms")
    parser.add_argument('-result_dir', dest='result_dir', default=result_folder(),
                        help='Directory for uploading '
                             'experiment results')
    algo_name = algo_impl.ALGO_PROBLEM.keys()
    parser.add_argument('-algo', dest='algo', required=True, choices=algo_name,
                        help='Algorithm implementation that will be measured')
    parser.add_argument('-config', dest='config', default=None, help='Config file for benchmark')
    parser.add_argument('-data_dir', dest='data_dir', required=True, help='Directory where dataset')
    parser.add_argument('-with_paths', dest='with_paths', type=bool, default=False, help='Is it necessary to measure '
                                                                                         'the extraction of paths?')
    parser.add_argument('-round', dest='rounds', type=int, default=5, help='Number of rounds for benchmarking')
    args = parser.parse_args()
    benchmark(args.algo, Path(args.data_dir), Path(args.result_dir), args.config, args.with_paths, args.rounds)
