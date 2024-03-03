import re
import shlex
import subprocess
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
        pass


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
    def command(self) -> Optional[str]:
        if self.base_command is None:
            return None
        else:
            return (f'/usr/bin/time -f "Ram usage in KB: %M;\n" -o /dev/stdout '
                    + ('' if self.timeout_sec is None else f'timeout {self.timeout_sec}s ')
                    + self.base_command)

    def run(self) -> CflrToolRunResult:
        if self.command is None:
            raise IncompatibleCflrToolError()
        process = subprocess.run(
            shlex.split(self.command),
            cwd=self.work_dir,
            stdout=subprocess.PIPE,
            text=True,
        )
        return self.parse_results(process)

    @abstractmethod
    def parse_results(self, process: subprocess.CompletedProcess[str]) -> CflrToolRunResult:
        pass

    @staticmethod
    def parse_ram_usage_kb(process: subprocess.CompletedProcess[str]) -> float:
        return float(re.search(r"Ram usage in KB: ([\d.]+);\n", process.stdout).group(1))

    @property
    def work_dir(self) -> Optional[Path]:
        return None
