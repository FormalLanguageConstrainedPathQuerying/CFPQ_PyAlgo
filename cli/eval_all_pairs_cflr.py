import argparse
import csv
import os
import shlex
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

from cli.all_pairs_cflr_command_manager import get_all_pairs_cflr_command_manager

# see `man timeout`
TIMEOUT_EXIT_CODE = 124


def check_file_for_completion(result_file_path, rounds):
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
    timeout: Optional[int],
    result_file_path: Path
):
    graph_base_name = graph_path.stem
    grammar_base_name = grammar_path.stem

    if not os.path.exists(result_file_path):
        with open(result_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["algo", "graph", "grammar", "edge_count", "ram_kb", "time_sec"])

    if "--rewrite-grammar" in algo_settings:
        algo_settings = algo_settings.replace("--rewrite-grammar", "")
        rewritten_grammar_path = grammar_path.with_stem(grammar_path.stem + "_rewritten")
        if os.path.exists(rewritten_grammar_path):
            grammar_path = rewritten_grammar_path

    for _ in range(rounds):
        if check_file_for_completion(result_file_path, rounds):
            return

        command_manager = get_all_pairs_cflr_command_manager(algo_settings, graph_path, grammar_path)

        temp_ram_file = Path("temp_ram_usage.txt").absolute()

        base_command = command_manager.create_command()

        if base_command is None:
            edge_count, ram_kb, time_sec = "-", "-", "-"
        else:
            command = (f"/usr/bin/time -o {temp_ram_file} -f %M "
                       + ("" if timeout is None else f"timeout {timeout}s ")
                       + base_command)

            process = subprocess.Popen(
                shlex.split(command),
                cwd=command_manager.work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL if command_manager.discard_stderr() else None
            )
            try:
                output, _ = process.communicate()
            except KeyboardInterrupt:
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                raise
            if process.returncode == 0:
                output = output.decode()
                time_sec = command_manager.get_analysis_time(output)
                edge_count = command_manager.get_edge_count(output)
                with open(temp_ram_file, 'r') as f:
                    ram_kb = f.read().strip()
            elif process.returncode == TIMEOUT_EXIT_CODE:
                print("    Runner process timed out")
                edge_count, ram_kb, time_sec = "OOT", "OOT", "OOT"
            else:
                print(
                    f"   Runner process terminated with return code {process.returncode}\n"
                    f"   (interpreting as out of memory error)"
                )
                edge_count, ram_kb, time_sec = "OOM", "OOM", "OOM"

        with open(result_file_path, 'a', newline='') as csvfile:
            print(f"   {edge_count} {ram_kb} {time_sec}")
            writer = csv.writer(csvfile)
            writer.writerow([
                {algo_name},
                os.path.basename(graph_base_name),
                os.path.basename(grammar_base_name),
                edge_count,
                ram_kb,
                time_sec
            ])


def eval_all_pairs_cflr(
    algo_config: Path,
    data_config: Path,
    result_path: Path,
    rounds: Optional[int],
    timeout: Optional[int],
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
                        timeout=timeout,
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
        timeout=args.timeout
    )


if __name__ == "__main__":       # pragma: no cover
    main(raw_args=sys.argv[1:])  # pragma: no cover
