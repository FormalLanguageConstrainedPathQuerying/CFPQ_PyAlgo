import argparse
import csv
import os
import re
import shlex
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from math import floor, log10
from pathlib import Path
from typing import Optional, List, Literal

import pandas as pd

DISPLAY_STD_THRESHOLD = 0.01

# see `man timeout`
TIMEOUT_EXIT_CODE = 124

class CflrDecomposerResult(ABC):
    @abstractmethod
    def get_data(self) -> list[str]:
        """All columns for CSV, as strings."""

    @abstractmethod
    def __repr__(self) -> str:
        pass

@dataclass
class CflrDecomposerSuccess(CflrDecomposerResult):
    s_edges: int
    ram_kb: float
    solver_time_sec: float
    decomposer_time_sec: float
    compression_factor: float
    is_compression_valid: bool

    def get_data(self) -> list[str]:
        return [str(v) for v in asdict(self).values()]

    def __repr__(self) -> str:
        return (f"s_edges={self.s_edges},"
                f"ram_kb={round_to_significant_digits(self.ram_kb)},"
                f"solver_sec={round_to_significant_digits(self.solver_time_sec)},"
                f"decomposer_sec={round_to_significant_digits(self.decomposer_time_sec)},"
                f"compression={round_to_significant_digits(self.compression_factor)},"
                f"valid={self.is_compression_valid}")


@dataclass
class CflrDecomposerError(CflrDecomposerResult):
    code: Literal["skipped", "OOT", "OOM"]

    def get_data(self) -> list[str]:
        # fill every column with the same code
        return [self.code] * len(CflrDecomposerSuccess.__dataclass_fields__)

    def __repr__(self) -> str:
        return f"error={self.code}"


def is_enough_data_collected(result_file_path: Path, rounds: int):
    try:
        with open(result_file_path, 'r', encoding="utf-8") as file:
            reader = list(csv.reader(file))
            if len(reader) - 1 >= rounds or any(
                    "OOT" in row or "OOM" in row or "-" in row
                    for row in reader
            ):
                return True
    except FileNotFoundError:
        pass
    return False

def do_single_decomposer_run(
    graph_path: Path,
    grammar_path: Path,
    timeout_sec: Optional[int]
) -> CflrDecomposerResult:
    try:
        process = subprocess.run(
            shlex.split(
                '/usr/bin/time -f "Ram usage in KB: %M;\n" -o /dev/stdout ' +
                ('' if timeout_sec is None else f'timeout --kill-after=3m {timeout_sec}s ') +
                f'python3 -m cfpq_decomposer_cli.decompose_cflr_matrix {graph_path} {grammar_path}'
            ),
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        return CflrDecomposerSuccess(
            s_edges=int(re.search(r"#(SEdges|CountEdges)\s+(\d+)", process.stdout).group(2)),
            ram_kb=float(re.search(r"Ram usage in KB: ([\d.]+);\n", process.stdout).group(1)),
            solver_time_sec=float(re.search(r"AnalysisTime\s+([\d.]+)", process.stdout).group(1)),
            decomposer_time_sec=float(re.search(r"Decomposition time\s+([\d.]+)", process.stdout).group(1)),
            compression_factor=float(re.search(r"Compression factor\s+([\d.]+)", process.stdout).group(1)),
            is_compression_valid=re.search(
                r"Is compression valid\s+(True|False)", process.stdout
            ).group(1) == str(True),
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == TIMEOUT_EXIT_CODE:
            print("    Runner process timed out")
            return CflrDecomposerError("OOT")
        else:
            print(
                f"   Runner process terminated with return code {e.returncode}\n"
                f"   (interpreting as out of memory error)"
            )
            return CflrDecomposerError("OOM")

def run_experiment(
        graph_path: Path,
        grammar_path: Path,
        rounds: int,
        timeout_sec: Optional[int],
        result_file_path: Path
):
    if not os.path.exists(result_file_path):
        result_file_path.parent.mkdir(exist_ok=True)
        with open(result_file_path, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "graph", "grammar", "s_edges", "ram_kb", "solver_time_sec",
                "decomposer_time_sec", "compression_factor", "is_compression_valid"
            ])

    if is_enough_data_collected(result_file_path, rounds):
        print(f"    Enough data has already been saved to {result_file_path}")
        return

    for _ in range(rounds):
        if is_enough_data_collected(result_file_path, rounds):
            return

        running_file_path = result_file_path.with_suffix('.unfinished')
        result: CflrDecomposerResult
        try:
            if os.path.isfile(running_file_path) and not user_confirms_rerun():
                result = CflrDecomposerError("skipped")
            else:
                with open(running_file_path, 'w', encoding="utf-8") as running_file:
                    running_file.write("CFPQ solver started, but has not yet finished")
                result = do_single_decomposer_run(
                    graph_path=graph_path,
                    grammar_path=grammar_path,
                    timeout_sec=timeout_sec
                )
        finally:
            os.remove(running_file_path)
        with open(result_file_path, 'a', newline='', encoding="utf-8") as csvfile:
            print(f"    {result}")
            writer = csv.writer(csvfile)
            writer.writerow([
                os.path.basename(graph_path.stem),
                os.path.basename(grammar_path.stem),
                *result.get_data()
            ])

def user_confirms_rerun() -> bool:
    while True:
        print(
            "Last time you run on this input experiment was stopped abruptly "
            "either because you stopped it manually or because container has crashed. "
            "Do you want to rerun the experiment on this input? (y/n)"
        )
        user_confirm = input().lower()
        if user_confirm == "y":
            return True
        if user_confirm == "n":
            return False

def round_to_significant_digits(x: float, digits: int = 2) -> float:
    if x == 0.0:
        return 0.0
    absolute_digits = -int(floor(log10(abs(x)))) + digits - 1
    return round(x, absolute_digits) if absolute_digits > 0 else int(round(x))

def format_metric(series: pd.Series) -> str:
    mean = series.mean()
    std = series.std(ddof=1) if len(series) > 1 else 0.0

    if std < DISPLAY_STD_THRESHOLD * mean:
        return str(round_to_significant_digits(mean))
    pct = int(std / mean * 100)
    return f"{round_to_significant_digits(mean)} ± {pct}%"

def reduce_results_to_one_row(result_file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(result_file_path)

    assert df['graph'].nunique() <= 1, "Multiple graphs found"
    assert df['grammar'].nunique() <= 1, "Multiple grammars found"

    df['ram_gb'] = df['ram_kb'].apply(
        lambda x: x / 10 ** 6 if isinstance(x, (int, float)) else x
    )

    if pd.to_numeric(df["s_edges"], errors="coerce").isna().any():
        row = df[pd.to_numeric(df["s_edges"], errors="coerce").isna()].iloc[0]
        cols = [
            "graph", "grammar", "s_edges",
            "ram_gb", "solver_time_sec", "decomposer_time_sec",
            "compression_factor", "is_compression_valid"
        ]
        return pd.DataFrame([row[cols].to_dict()])

    return pd.DataFrame({
        "graph": [df["graph"].iat[0]],
        "grammar": [df["grammar"].iat[0]],
        "s_edges": [df["s_edges"].iat[0]],
        "ram_gb": [format_metric(df["ram_gb"])],
        "solver_time_sec": [format_metric(df["solver_time_sec"])],
        "decomposer_time_sec": [format_metric(df["decomposer_time_sec"])],
        "compression_factor": [format_metric(df["compression_factor"])],
        "is_compression_valid": [f"{int(df['is_compression_valid'].sum())}/{len(df)}"]
    })

def pprint_df(df: pd.DataFrame, title: str):
    df_string = df.to_markdown(maxheadercolwidths=12, maxcolwidths=12)
    width = max(len(line) for line in df_string.splitlines())
    print(title.center(width, "="))
    print(df_string)
    print("=" * width)


def min_numeric(series: pd.Series) -> float:
    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    return float('inf') if numeric_series.empty else numeric_series.min()

def format_int(x):
    try:
        return format(x, ',')
    except ValueError:
        return x


def display_results_for_grammar(df: pd.DataFrame, grammar: str):
    df = df[df['grammar'] == grammar].copy()
    df.drop(columns=['grammar'], inplace=True)
    pprint_df(df, f"Results for CFG '{grammar}'")

def display_results(result_files_paths: List[Path]) -> None:
    print()
    print("RESULTS:")
    print(f"Sample std is shown when it's over {DISPLAY_STD_THRESHOLD * 100}% of the mean.")
    print()

    df = pd.concat(
        [
            reduce_results_to_one_row(result_file_path)
            for result_file_path in result_files_paths
        ],
        ignore_index=True
    )
    with pd.option_context(
            'display.max_rows', None,
            'display.max_columns', None
    ):
        for grammar in df['grammar'].unique():
            display_results_for_grammar(df, grammar)
    print(f"Sample std is shown when it's over {DISPLAY_STD_THRESHOLD * 100}% of the mean.")


def eval_all_pairs_cflr(
        data_config: Path,
        result_path: Path,
        rounds: Optional[int],
        timeout_sec: Optional[int],
):
    result_files_paths = []
    with open(data_config, mode='r', encoding="utf-8") as data_file:
        data_reader = csv.DictReader(data_file)
        for data_row in data_reader:
            graph_path = Path(data_row['graph_path']).absolute()
            grammar_path = Path(data_row['grammar_path']).absolute()
            print(f"  Processing data: {graph_path.stem}, {grammar_path.stem}")
            result_file_name = f"{graph_path.stem}_{grammar_path.stem}.csv"
            result_file_path = Path(os.path.join(result_path, result_file_name))

            run_experiment(
                graph_path=graph_path,
                grammar_path=grammar_path,
                rounds=rounds,
                timeout_sec=timeout_sec,
                result_file_path=result_file_path
            )
            result_files_paths.append(result_file_path)
    display_results(result_files_paths)


def main(raw_args: List[str]):
    parser = argparse.ArgumentParser(
        description='Evaluates all vertex pairs '
                    'Context-Free Language Reachability (CFL-R) decomposition algorithms.'
    )
    parser.add_argument('data_config', type=str,
                        help='Path to the data-config csv file.')
    parser.add_argument('result_path', type=str,
                        help='Path to save the results.')
    parser.add_argument('--rounds', type=int, default=1,
                        help='Number of rounds to run each configuration.')
    parser.add_argument('--timeout', type=int, default=None,
                        help='Timeout for each run in seconds.')

    args = parser.parse_args(raw_args)
    eval_all_pairs_cflr(
        data_config=Path(args.data_config),
        result_path=Path(args.result_path),
        rounds=args.rounds,
        timeout_sec=args.timeout
    )


if __name__ == "__main__":  # pragma: no cover
    main(raw_args=sys.argv[1:])  # pragma: no cover
