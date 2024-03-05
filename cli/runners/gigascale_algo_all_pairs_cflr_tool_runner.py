import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Optional

from cli.runners.all_pairs_cflr_tool_runner import AbstractAllPairsCflrToolRunner, CflrToolRunResult, \
    IncompatibleCflrToolError


class GigascaleAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def base_command(self) -> Optional[str]:
        return (
            f'./run.sh -wdlrb -i datasets/dacapo9/{self.graph_path.stem}'
            if self.grammar_path.stem in {"java_points_to", "java_points_to_rewritten"}
            else None
        )

    @property
    def work_dir(self) -> Optional[Path]:
        return Path(os.environ['GIGASCALE_DIR'])

    def run(self) -> CflrToolRunResult:
        if self.base_command is None:
            raise IncompatibleCflrToolError()
        # Gigascale run script uses `bash -i -c`, which can't be used repeatedly
        # without emulating interactive environment with tools like `expect`.
        # Read more about `bash -ic` pitfalls:
        # https://stackoverflow.com/questions/39920915/unexpected-sigttin-after-bash-ic-bin-echo-hello-when-bash-scripting
        process = subprocess.run(
            shlex.split(self.timeout_command + "expect"),
            cwd=self.work_dir,
            stdout=subprocess.PIPE,
            text=True,
            check=True,
            input=
            f"""
            set timeout -1
            spawn {self.measure_ram_command + self.base_command}
            expect eof
            """
        )
        return self.safe_parse_results(process)

    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        # parses a table like this:
        # benchmark   TC-time  TC-mem  v       e       vpt     avg    max  load/f  store/f
        # tradebeans  3.5      1055    439693  466969  696316  1.584  581  517     144
        pattern = (r"benchmark\s+TC-time\s+TC-mem\s+v\s+e\s+vpt\s+avg\s+max\s+load/f\s+store/f\s*\n"
                   r"\w+\s+"
                   r"(\d+\.\d+)\s+"
                   r"\d+(?:\.\d+)?\s+"
                   r"\d+\s+"
                   r"\d+\s+"
                   r"(\d+)\s+"
                   r"\d+(?:\.\d+)?\s+"
                   r"\d+\s+"
                   r"\d+\s+"
                   r"\d+")

        tc_time, vpt = re.search(pattern, process.stdout).groups()

        return CflrToolRunResult(
            s_edges=int(vpt),
            time_sec=float(tc_time),
            ram_kb=self.parse_ram_usage_kb(process)
        )
