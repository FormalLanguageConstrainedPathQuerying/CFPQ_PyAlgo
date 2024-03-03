import re
import subprocess
from typing import Optional

from cli.runners.all_pairs_cflr_tool_runner import AbstractAllPairsCflrToolRunner, CflrToolRunResult


class PyAlgoAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def base_command(self) -> Optional[str]:
        return f"python3 -m cli.run_all_pairs_cflr {self.algo_settings} {self.graph_path} {self.grammar_path}"

    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        return CflrToolRunResult(
            s_edges=int(re.search(r"#(SEdges|CountEdges)\s+(\d+)", process.stdout).group(2)),
            time_sec=float(re.search(r"AnalysisTime\s+([\d.]+)", process.stdout).group(1)),
            ram_kb=self.parse_ram_usage_kb(process)
        )
