from pathlib import Path
from typing import Optional

from cli.runners.all_pairs_cflr_tool_runner import CflrToolRunResult
from cli.runners.gigascale_algo_all_pairs_cflr_tool_runner import GigascaleAllPairsCflrToolRunner
from cli.runners.graspan_algo_all_pairs_cflr_tool_runner import GraspanAllPairsCflrToolRunner
from cli.runners.pearl_algo_all_pairs_cflr_tool_runner import PearlAllPairsCflrToolRunner
from cli.runners.pocr_algo_all_pairs_cflr_tool_runner import PocrAllPairsCflrToolRunner
from cli.runners.py_algo_all_pairs_cflr_tool_runner import PyAlgoAllPairsCflrToolRunner


def run_appropriate_all_pairs_cflr_tool(
        algo_settings: str,
        graph_path: Path,
        grammar_path: Path,
        timeout_sec: Optional[int]
) -> CflrToolRunResult:
    return {
        "pocr": PocrAllPairsCflrToolRunner,
        "pearl": PearlAllPairsCflrToolRunner,
        "gigascale": GigascaleAllPairsCflrToolRunner,
        "graspan": GraspanAllPairsCflrToolRunner
    }.get(algo_settings, PyAlgoAllPairsCflrToolRunner)(
        algo_settings, graph_path, grammar_path, timeout_sec
    ).run()
