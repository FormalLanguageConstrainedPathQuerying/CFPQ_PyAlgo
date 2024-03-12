import os

import pytest

from cfpq_cli import run_all_pairs_cflr
from src.utils.useful_paths import POCR_FORMAT_DATA
from test.utils import find_grammar_file, find_graph_file, read_tuples_set


@pytest.mark.CI
def test_cli_run_all_pairs_cflr_out():
    data_path = os.path.join(POCR_FORMAT_DATA, 'transitive_line')
    actual_path = os.path.join(data_path, 'actual_all_pairs_reachability_via_cli.txt')
    expected_path = os.path.join(data_path, 'expected_all_pairs_reachability.txt')
    run_all_pairs_cflr.main(
        [
            'IncrementalAllPairsCFLReachabilityMatrix',
            find_graph_file(data_path),
            find_grammar_file(data_path),
            '--out', actual_path
        ]
    )
    with open(actual_path, 'r') as actual_file:
        with open(expected_path, 'r') as expected_file:
            actual = read_tuples_set(actual_file)
            expected = read_tuples_set(expected_file)
            assert actual == expected
