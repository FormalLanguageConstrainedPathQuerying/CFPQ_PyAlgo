import os
from unittest.mock import patch

import pytest

from cfpq_decomposer_cli.decompose_cflr_matrix import main as decompose_main
from src.utils.useful_paths import POCR_FORMAT_DATA
from test.cfpq_decomposer_cli.utils import parse_decomposer_cli_output, CorruptDecomposer
from test.utils import find_graph_file, find_grammar_file

EXPECTED_SEDGES = 3_968_276
DATA_PATH = os.path.join(POCR_FORMAT_DATA, 'leela')
GRAPH_PATH = find_graph_file(DATA_PATH)
GRAMMAR_PATH = find_grammar_file(DATA_PATH)


@pytest.mark.CI
@pytest.mark.parametrize(
    "args",
    [
        [],
        pytest.param(
            ["--prototype"],
            id="prototype",
            marks=pytest.mark.skip(
                reason="--prototype is too slow and already covered by unit tests"
            ),
        ),
    ],
    ids=["default", "prototype"],
)
def test_cli_decompose_cflr_matrix_modes(args, capsys):
    decompose_main([GRAPH_PATH, GRAMMAR_PATH] + args)
    captured = capsys.readouterr()
    metrics = parse_decomposer_cli_output(captured.out)

    assert metrics.s_edges == EXPECTED_SEDGES, f"#SEdges mismatch for args={args}"
    assert metrics.compression_factor > 10, f"Compression factor too low for args={args}"
    assert metrics.is_valid, f"Compression invalid for args={args}"

@pytest.mark.CI
@patch('cfpq_decomposer_cli.decompose_cflr_matrix.HighPerformanceDecomposer', new=CorruptDecomposer)
def test_cli_decompose_cflr_matrix_corrupted(monkeypatch, capsys):
    decompose_main([GRAPH_PATH, GRAMMAR_PATH])
    captured = capsys.readouterr()
    metrics = parse_decomposer_cli_output(captured.out)
    assert not metrics.is_valid, "Expected compression to be invalid when decomposer is corrupted"
