import os

import pytest

from cfpq_cli.run_all_pairs_cflr import run_all_pairs_cflr
from test.conftest import pocr_data_path
from test.utils import find_graph_file, find_grammar_file, read_tuples_set


@pytest.mark.CI
def test_all_pairs_cflr(algo_name, pocr_data_path, algo_settings):
    try:
        print()
        print(f"Algo: {algo_name}")
        print(f"Settings: {algo_settings}")
        print(f"Pocr data: {pocr_data_path}")

        actual_path = os.path.join(pocr_data_path, "actual_all_pairs_reachability.txt")
        expected_path = os.path.join(pocr_data_path, "expected_all_pairs_reachability.txt")
        run_all_pairs_cflr(
            algo_name=algo_name,
            graph_path=find_graph_file(pocr_data_path),
            grammar_path=find_grammar_file(pocr_data_path),
            settings=algo_settings,
            time_limit_sec=600,
            out_path=actual_path,
        )
        with open(actual_path, 'r') as actual_file:
            with open(expected_path, 'r') as expected_file:
                actual = read_tuples_set(actual_file)
                expected = read_tuples_set(expected_file)
                assert actual == expected
    finally:
        print()
