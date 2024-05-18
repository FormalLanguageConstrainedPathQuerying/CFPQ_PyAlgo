import os
import subprocess
import uuid
import warnings
from pathlib import Path
from typing import Optional

import pandas as pd
import psutil

from cfpq_eval.runners.all_pairs_cflr_tool_runner import (
    AbstractAllPairsCflrToolRunner,
    CflrToolRunResult
)
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph
from cfpq_model.model_utils import explode_indices

_WARM_UP_ROUNDS = 1


class KotgllAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.timeout_sec is not None:
            self.timeout_sec += _WARM_UP_ROUNDS * self.timeout_sec

    @property
    def base_command(self) -> Optional[str]:
        grammar = CnfGrammarTemplate.read_from_pocr_cnf_file(self.grammar_path)
        graph = LabelDecomposedGraph.read_from_pocr_graph_file(self.graph_path)

        grammar_path = self.grammar_path.parent / "kotgll" / (self.grammar_path.stem + ".rsm")
        if not os.path.isfile(grammar_path):
            grammar_path = grammar_path.with_suffix(".cfg")
            if not os.path.isfile(grammar_path):
                warnings.warn(
                    "Skipping kotgll evaluation, because RSM/CFG is missing. "
                    "To fix this error write RSM/CFG to "
                    f"'{grammar_path.with_suffix('.rsm')}' or '{grammar_path.with_suffix('.cfg')}'. "
                    "See https://github.com/vadyushkins/kotgll?tab=readme-ov-file#rsm-format-example"
                )
                return None
        if graph.block_matrix_space.block_count > 1:
            exploded_grammar_path = (
                    self.grammar_path.parent / "kotgll" / self.grammar_path.stem /
                    self.graph_path.stem / (self.grammar_path.stem + grammar_path.suffix)
            )
            self._explode_grammar(
                grammar_path,
                exploded_grammar_path,
                graph.block_matrix_space.block_count
            )
            grammar_path = exploded_grammar_path

        # kotgll doesn't support indexed symbols, we need to concat labels and indices
        graph, grammar = explode_indices(graph, grammar)
        graph_path = self.graph_path.parent / "kotgll" / self.graph_path.stem / self.graph_path.name
        os.makedirs(graph_path.parent, exist_ok=True)
        # kotgll requires its own graph formatting, so we need to save the graph in a custom format
        self._write_kotgll_graph(graph, graph_path)

        out_folder = self.graph_path.parent / "kotgll" / 'out' / str(uuid.uuid4())
        os.makedirs(out_folder)

        return (
            f'java -Xmx{self._get_max_memory_gb()}G '
            '-cp kotgll.jar org.kotgll.benchmarks.BenchmarksKt '
            f'--grammar {grammar_path.suffix[1:]} --sppf off '
            f'--inputPath {graph_path.parent} --grammarPath {grammar_path} '
            f'--outputPath {out_folder} '
            f'--warmUpRounds {_WARM_UP_ROUNDS} --benchmarkRounds 1'
        )

    @property
    def work_dir(self) -> Optional[Path]:
        return Path(os.environ['KOTGLL_DIR'])

    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        for line in process.stdout.split('\n'):
            if line.startswith('benchmark::'):
                parts = line.split()
                return CflrToolRunResult(
                    s_edges=int(parts[-2]),
                    time_sec=float(parts[-1]),
                    ram_kb=self.parse_ram_usage_kb(process)
                )
        raise Exception(f"No results are found in stdout {process.stdout}")

    @staticmethod
    def _write_kotgll_graph(graph: LabelDecomposedGraph, graph_path: Path) -> None:
        with open(graph_path, 'w', encoding="utf-8") as output_file:
            for symbol, matrix in graph.matrices.items():
                edge_label = symbol.label
                rows = matrix.npI
                columns = matrix.npJ
                edges_df = pd.DataFrame({
                    'source': rows,
                    'destination': columns,
                    'label': edge_label
                })
                csv_string = edges_df.to_csv(sep=' ', index=False, header=False)
                output_file.write(csv_string)

    @staticmethod
    def _explode_grammar(rsm_path: Path, exploded_grammar_path: Path, block_count: int) -> None:
        os.makedirs(exploded_grammar_path.parent, exist_ok=True)
        with open(rsm_path, 'r') as infile, open(exploded_grammar_path, 'w') as outfile:
            for line in infile:
                if '{' in line and '}' in line:
                    for i in range(block_count + 1):
                        expanded_line = eval(f"f'{line.strip()}'")
                        outfile.write(expanded_line + '\n')
                else:
                    outfile.write(line)

    @staticmethod
    def _get_max_memory_gb():
        mem_bytes = psutil.virtual_memory().total
        mem_gb = mem_bytes / (1024 ** 3)
        return int(mem_gb * 0.9)
