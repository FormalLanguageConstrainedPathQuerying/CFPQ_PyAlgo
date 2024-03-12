import os
import re
import subprocess
from pathlib import Path
from typing import Optional

import psutil

from cfpq_eval.runners.all_pairs_cflr_tool_runner import AbstractAllPairsCflrToolRunner, CflrToolRunResult
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph
from cfpq_model.utils import explode_indices


class GraspanAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def base_command(self) -> Optional[str]:
        grammar = CnfGrammarTemplate.read_from_pocr_cnf_file(self.grammar_path)
        graph = LabelDecomposedGraph.read_from_pocr_graph_file(self.graph_path)

        # Graspan doesn't support indexed symbols, we need to concat labels and indices
        if graph.block_matrix_space.block_count > 1:
            graph, grammar = explode_indices(graph, grammar)
            graph_path = self.graph_path.parent / "graspan" / self.graph_path.name
            os.makedirs(graph_path.parent, exist_ok=True)
            graph.write_to_pocr_graph_file(graph_path)
        else:
            graph_path = self.graph_path

        # Graspan doesn't support grammars with over 255 symbols, because
        # each symbol is encoded with one byte and one symbol is reserved for epsilon
        if len(grammar.symbols) > 255:
            return None

        grammar_path = self.grammar_path.parent / "graspan" / self.grammar_path.name
        os.makedirs(grammar_path.parent, exist_ok=True)
        grammar.write_to_pocr_cnf_file(grammar_path, include_starting=False)

        return (
            f'./run {graph_path} {grammar_path} 1 '
            f'{int(psutil.virtual_memory().total / 10**9 * 0.9)} '
            f'{os.cpu_count() * 2}'
        )

    @property
    def work_dir(self) -> Optional[Path]:
        return Path(os.environ['GRASPAN_DIR']) / "src"

    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        final_file = re.search(r"finalFile:\s*(.*)", process.stdout).group(1)
        start_nonterm = CnfGrammarTemplate.read_from_pocr_cnf_file(self.grammar_path).start_nonterm
        with open(final_file, "r") as file:
            s_edges = set()
            for line in file:
                if line.split()[-1] == start_nonterm.label:
                    s_edges.add((line.split()[0], line.split()[1]))

        return CflrToolRunResult(
            s_edges=len(s_edges),
            time_sec=float(re.search(r"COMP TIME:\s*([\d.]+|NaN)", process.stdout).group(1)),
            ram_kb=self.parse_ram_usage_kb(process)
        )
