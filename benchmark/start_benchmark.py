import argparse
from pathlib import Path
import os
import datetime

from benchmark.algo_impl import *
from benchmark.bench import benchmark


def result_folder():
    """
    Creates and returns an unused result directory
    @return: path to new directory
    """
    results = 'results'
    if not os.path.exists(results):
        os.mkdir(f'results')

    now = datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')
    result_folder = os.path.join(results, now)

    os.mkdir(result_folder)
    return result_folder


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark implementations CFPQ's algorithms")
    ms_algo_name = ALGO_PROBLEM.keys()
    parser.add_argument('-ms_algo', dest='ms_algo', required=True, choices=ms_algo_name,
                        help='Multiple sources algorithm implementation that will be measured')
    parser.add_argument('-data_dir', dest='data_dir', required=True,
                        help='Directory where dataset')
    parser.add_argument('-result_dir', dest='result_dir', default=result_folder(),
                        help='Directory for uploading experiment results')
    parser.add_argument('-all_pairs_rounds', dest='all_pairs_rounds', type=int, default=5,
                        help='Number of rounds for benchmarking all pairs (Default: all_pairs_rounds = 5)')
    parser.add_argument('-ms_worst_rounds', dest='ms_worst_rounds', type=int, default=5,
                        help='Number of rounds for benchmarking ms worst result (Default: ms_worst_rounds = 5)')
    parser.add_argument('-ms_min_reachable_vertices', dest='ms_min_reachable_vertices', type=int, default=1,
                        help='Minimal number of reachable vertices for benchmarking ms (Default: ms_min_reachable_vertices = 1)')
    parser.add_argument('-ms_worst_count', dest='ms_worst_count', type=int, default=5,
                        help='Number of vertices for benchmarking ms worst result (Default: ms_worst_count = 5)')

    args = parser.parse_args()

    benchmark(args.all_pairs_rounds,
              args.ms_algo,
              args.ms_min_reachable_vertices,
              args.ms_worst_rounds,
              args.ms_worst_count,
              Path(args.data_dir),
              Path(args.result_dir))
