import re
import subprocess
from typing import Optional

from cfpq_eval.runners.all_pairs_cflr_tool_runner import (
    AbstractAllPairsCflrToolRunner,
    CflrToolRunResult
)


class PyAlgoAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    @property
    def base_command(self) -> Optional[str]:
        return ("python3 -m cli.run_all_pairs_cflr "
                f"{self.algo_settings} {self.graph_path} {self.grammar_path}")

    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        return CflrToolRunResult(
            s_edges=int(re.search(r"#(SEdges|CountEdges)\s+(\d+)", process.stdout).group(2)),
            time_sec=float(re.search(r"AnalysisTime\s+([\d.]+)", process.stdout).group(1)),
            ram_kb=self.parse_ram_usage_kb(process)
        )
