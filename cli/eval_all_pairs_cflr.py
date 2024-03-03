import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

from cli.runners.all_pairs_cflr_tool_runner import IncompatibleCflrToolError
from cli.runners.all_pairs_cflr_tool_runner_facade import run_appropriate_all_pairs_cflr_tool

# see `man timeout`
TIMEOUT_EXIT_CODE = 124


def is_enough_data_collected(result_file_path, rounds):
    try:
        with open(result_file_path, 'r') as file:
            reader = list(csv.reader(file))
            if len(reader) - 1 >= rounds or any("OOT" in row or "OOM" in row for row in reader):
                return True
    except FileNotFoundError:
        pass
    return False


def run_experiment(
    algo_settings: str,
    algo_name: str,
    graph_path: Path,
    grammar_path: Path,
    rounds: int,
    timeout_sec: Optional[int],
    result_file_path: Path
):
    graph_base_name = graph_path.stem
    grammar_base_name = grammar_path.stem

    if not os.path.exists(result_file_path):
        with open(result_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["algo", "graph", "grammar", "s_edges", "ram_kb", "time_sec"])

    if "--rewrite-grammar" in algo_settings:
        algo_settings = algo_settings.replace("--rewrite-grammar", "")
        rewritten_grammar_path = grammar_path.with_stem(grammar_path.stem + "_rewritten")
        if os.path.exists(rewritten_grammar_path):
            grammar_path = rewritten_grammar_path

    for _ in range(rounds):
        if is_enough_data_collected(result_file_path, rounds):
            return

        try:
            result = run_appropriate_all_pairs_cflr_tool(
                algo_settings=algo_settings,
                graph_path=graph_path,
                grammar_path=grammar_path,
                timeout_sec=timeout_sec
            )
            s_edges = result.s_edges
            ram_kb = result.ram_kb
            time_sec = result.time_sec
        except IncompatibleCflrToolError:
            s_edges, ram_kb, time_sec = "-", "-", "-"
        except subprocess.CalledProcessError as e:
            if e.returncode == TIMEOUT_EXIT_CODE:
                print("    Runner process timed out")
                s_edges, ram_kb, time_sec = "OOT", "OOT", "OOT"
            else:
                print(
                    f"   Runner process terminated with return code {e.returncode}\n"
                    f"   (interpreting as out of memory error)"
                )
                s_edges, ram_kb, time_sec = "OOM", "OOM", "OOM"

        with open(result_file_path, 'a', newline='') as csvfile:
            print(f"   {s_edges} {ram_kb} {time_sec}")
            writer = csv.writer(csvfile)
            writer.writerow([
                {algo_name},
                os.path.basename(graph_base_name),
                os.path.basename(grammar_base_name),
                s_edges,
                ram_kb,
                time_sec
            ])


def eval_all_pairs_cflr(
    algo_config: Path,
    data_config: Path,
    result_path: Path,
    rounds: Optional[int],
    timeout_sec: Optional[int],
):
    with open(algo_config, mode='r') as algo_file:
        algo_reader = csv.DictReader(algo_file)
        for algo_row in algo_reader:
            algo_name = algo_row['algo_name']
            print(f"Running algorithm: {algo_name}")
            algo_settings = algo_row['algo_settings']
            algo_result_path = os.path.join(result_path, algo_name)
            if not os.path.exists(algo_result_path):
                os.makedirs(algo_result_path)

            with open(data_config, mode='r') as data_file:
                data_reader = csv.DictReader(data_file)
                for data_row in data_reader:
                    graph_path = Path(data_row['graph_path']).absolute()
                    grammar_path = Path(data_row['grammar_path']).absolute()
                    print(f"  Processing data: {graph_path.stem}, {grammar_path.stem}")
                    result_file_name = f"{graph_path.stem}_{grammar_path.stem}.csv"
                    result_file_path = Path(os.path.join(algo_result_path, result_file_name))

                    run_experiment(
                        algo_settings=algo_settings,
                        algo_name=algo_name,
                        graph_path=graph_path,
                        grammar_path=grammar_path,
                        rounds=rounds,
                        timeout_sec=timeout_sec,
                        result_file_path=result_file_path
                    )


def main(raw_args: List[str]):
    parser = argparse.ArgumentParser(
        description='Evaluates all vertex pairs Context-Free Language Reachability (CFL-R) algorithms.'
    )

    parser.add_argument('algo_config', type=str,
                        help='Path to the algo-config csv file.')
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
        algo_config=Path(args.algo_config),
        data_config=Path(args.data_config),
        result_path=Path(args.result_path),
        rounds=args.rounds,
        timeout_sec=args.timeout
    )


if __name__ == "__main__":       # pragma: no cover
    main(raw_args=sys.argv[1:])  # pragma: no cover
