import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from cfpq_eval.runners.all_pairs_cflr_tool_runner import (
    AbstractAllPairsCflrToolRunner, CflrToolRunResult
)


class PearlAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    @property
    def base_command(self) -> Optional[str]:
        return (
            f'./{self.grammar_path.stem} {self.graph_path} -pearl -scc=false -gf=false'
            if self.grammar_path.stem in {"aa", "vf"}
            else None
        )

    @property
    def work_dir(self) -> Optional[Path]:
        return Path(os.environ['PEARL_DIR'])

    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        return CflrToolRunResult(
            s_edges=self.parse_s_edges(process),
            time_sec=float(re.search(r"AnalysisTime\s+([\d.]+)", process.stdout).group(1)),
            ram_kb=self.parse_ram_usage_kb(process)
        )

    @staticmethod
    def parse_s_edges(process: subprocess.CompletedProcess[str]) -> int:
        vedges_search = re.search(r"#VEdges\s+(\d+)", process.stdout)
        if vedges_search:
            return vedges_search.group(1)
        return re.search(r"#AEdges\s+(\d+)", process.stdout).group(1)
