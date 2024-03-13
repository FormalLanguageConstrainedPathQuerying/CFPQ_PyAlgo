import re
import shlex
import subprocess
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CflrToolRunResult:
    s_edges: int
    time_sec: float
    ram_kb: float


class IncompatibleCflrToolError(Exception):
    pass


class AllPairsCflrToolRunner(ABC):
    @abstractmethod
    def run(self) -> CflrToolRunResult:
        """
        Raises IncompatibleCflrToolError if CFL-r tool can't process this kind of input.
        For example, some tools are only compatible with one specific grammar.

        Raises CalledProcessError if CFL-r exits with non-zero exit code.
        """


class AbstractAllPairsCflrToolRunner(AllPairsCflrToolRunner, ABC):
    def __init__(
            self,
            algo_settings: str,
            graph_path: Path,
            grammar_path: Path,
            timout_sec: Optional[int]
    ):
        self.algo_settings = algo_settings
        self.graph_path = graph_path
        self.grammar_path = grammar_path
        self.timeout_sec = timout_sec

    @property
    @abstractmethod
    def base_command(self) -> Optional[str]:
        pass

    @property
    def timeout_command(self) -> str:
        return '' if self.timeout_sec is None else f'timeout {self.timeout_sec}s '

    @property
    def measure_ram_command(self) -> str:
        return '/usr/bin/time -f "Ram usage in KB: %M;\n" -o /dev/stdout '

    def run(self) -> CflrToolRunResult:
        if self.base_command is None:
            raise IncompatibleCflrToolError()
        process = subprocess.run(
            shlex.split(
                self.measure_ram_command + self.timeout_command + self.base_command
            ),
            cwd=self.work_dir,
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        return self.safe_parse_results(process)

    def safe_parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        try:
            return self.parse_results(process)
        except Exception as exc:
            print(
                "   Failed to parse results\n"
                "   (interpreting as incompatible CFL-r tool error)"
            )
            print("=====")
            print("stdout:")
            print(process.stdout)
            print("=====")
            print("stderr:")
            print(process.stderr)
            print("=====")
            traceback.print_exc()
            print("=====")
            raise IncompatibleCflrToolError() from exc

    @abstractmethod
    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        pass

    @staticmethod
    def parse_ram_usage_kb(process: subprocess.CompletedProcess[str]) -> float:
        return float(re.search(r"Ram usage in KB: ([\d.]+);\n", process.stdout).group(1))

    @property
    def work_dir(self) -> Optional[Path]:
        return None
