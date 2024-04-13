import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Optional

from cfpq_eval.runners.all_pairs_cflr_tool_runner import (
    AbstractAllPairsCflrToolRunner,
    CflrToolRunResult,
    IncompatibleCflrToolError
)


class GigascaleAllPairsCflrToolRunner(AbstractAllPairsCflrToolRunner):
    @property
    def base_command(self) -> Optional[str]:
        if self.grammar_path.stem not in {"java_points_to", "java_points_to_rewritten"}:
            return None
        base_path = os.path.dirname(self.graph_path)
        gigascale_path = os.path.join(base_path, 'Gigascale')
        adapted_graph_path = os.path.join(gigascale_path, self.graph_path.stem)
        os.makedirs(adapted_graph_path, exist_ok=True)

        alloc_path = os.path.join(adapted_graph_path, 'Alloc.csv')
        assign_path = os.path.join(adapted_graph_path, 'Assign.csv')
        load_path = os.path.join(adapted_graph_path, 'Load.csv')
        store_path = os.path.join(adapted_graph_path, 'Store.csv')

        with open(alloc_path, 'w') as alloc_file, \
                open(assign_path, 'w') as assign_file, \
                open(load_path, 'w') as load_file, \
                open(store_path, 'w') as store_file:

            with open(self.graph_path, 'r') as graph_file:
                for line in graph_file:
                    line_data = line.strip().split()
                    if len(line_data) == 0:
                        continue

                    source, target, label = line_data[:3]
                    # NOTE: It's not a mistake that `target` and `source` are sometimes swapped
                    # The swap is required to get an answer consistent with other tools.
                    if label == 'alloc':
                        alloc_file.write(f'"var_{source}","var_{target}"\n')
                    elif label == 'assign':
                        assign_file.write(f'"var_{target}","var_{source}"\n')
                    elif label == 'load_i':
                        field = line_data[3]
                        load_file.write(f'"var_{target}","var_{source}","field_{field}"\n')
                    elif label == 'store_i':
                        field = line_data[3]
                        store_file.write(f'"var_{target}","var_{source}","field_{field}"\n')
                    else:
                        assert "_r" in label, (f"Label '{label} must be 'alloc', 'assign' "
                                               f"or 'load_i' or 'store_i' or contain '_r")
        return f'./run.sh -wdlrb -i {adapted_graph_path}'

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
            input=f"""
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
