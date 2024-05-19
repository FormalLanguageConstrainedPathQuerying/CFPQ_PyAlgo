import os
import re
import subprocess
from pathlib import Path
from typing import Optional

import pandas as pd

from cfpq_eval.runners.all_pairs_cflr_tool_runner import (
    AbstractAllPairsCflrToolRunner, CflrToolRunResult
)
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate, Symbol
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph
from cfpq_model.model_utils import explode_indices


class LegacyMatrixAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    @property
    def base_command(self) -> Optional[str]:
        grammar = CnfGrammarTemplate.read_from_pocr_cnf_file(self.grammar_path)
        graph = LabelDecomposedGraph.read_from_pocr_graph_file(self.graph_path)

        # Legacy Matrix doesn't support indexed symbols, we need to concat labels and indices
        graph, grammar = explode_indices(graph, grammar)
        graph_path = self.graph_path.parent / "legacy_matrix" / self.graph_path.name
        os.makedirs(graph_path.parent, exist_ok=True)
        self._write_legacy_graph(graph, graph_path)
        grammar_path = self.grammar_path.parent / "legacy_matrix" / self.grammar_path.name
        os.makedirs(grammar_path.parent, exist_ok=True)
        self._write_legacy_grammar(grammar, grammar_path)
        return f"python3 -m src.legacy_cflr {graph_path} {grammar_path}"

    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        return CflrToolRunResult(
            s_edges=int(re.search(r"#(SEdges|CountEdges)\s+(\d+)", process.stdout).group(2)),
            time_sec=float(re.search(r"AnalysisTime\s+([\d.]+)", process.stdout).group(1)),
            ram_kb=self.parse_ram_usage_kb(process)
        )

    @staticmethod
    def _write_legacy_graph(graph: LabelDecomposedGraph, graph_path: Path) -> None:
        with open(graph_path, 'w', encoding="utf-8") as output_file:
            for symbol, matrix in graph.matrices.items():
                edge_label = symbol.label
                (rows, columns, _) = matrix.to_coo()
                edges_df = pd.DataFrame({
                    'source': rows,
                    'label': edge_label,
                    'destination': columns,
                })
                csv_string = edges_df.to_csv(sep=' ', index=False, header=False)
                output_file.write(csv_string)

    @staticmethod
    def _write_legacy_grammar(grammar: CnfGrammarTemplate, grammar_path: Path) -> None:
        with (open(grammar_path, 'w', encoding="utf-8") as output_file):
            output_file.write(f"{grammar.start_nonterm.label}\n\n")

            non_terms = grammar.non_terminals
            non_term_prefix = "NON_TERMINAL#"
            eps = f"{non_term_prefix}EPS"

            terms_needing_non_term = set()
            eps_needed = False

            def format(symbol: Symbol) -> str:
                if symbol in non_terms:
                    return symbol.label
                else:
                    terms_needing_non_term.add(symbol)
                    return f"{non_term_prefix}{symbol.label}"

            for lhs in grammar.epsilon_rules:
                output_file.write(f"{lhs.label} ->\n")
            for lhs, rhs in grammar.simple_rules:
                # Legacy Matrix doesn't support rules with
                # single non-terminal right-hand side (see CnfGrammar).
                # Hence, we need to add auxiliary EPS non-terminal.
                if rhs in non_terms:
                    output_file.write(f"{lhs.label} -> {rhs.label} {eps}\n")
                    eps_needed = True
                else:
                    output_file.write(f"{lhs} -> {rhs.label}\n")
            for lhs, rhs1, rhs2 in grammar.complex_rules:
                # Legacy Matrix doesn't support terminals in complex rules (see CnfGrammar).
                # Hence, we need to add auxiliary non-terminals (see the next `for` loop).
                output_file.write(f"{lhs} -> {format(rhs1)} {format(rhs2)}\n")

            for term in terms_needing_non_term:
                output_file.write(f"{non_term_prefix}{term.label} -> {term.label}\n")

            if eps_needed:
                output_file.write(f"{eps} ->\n")
