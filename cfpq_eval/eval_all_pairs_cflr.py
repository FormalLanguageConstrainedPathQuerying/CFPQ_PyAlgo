import argparse
import csv
import os
import subprocess
import sys
import warnings
from math import floor, log10
from pathlib import Path
from typing import Optional, List

import pandas as pd

from cfpq_eval.runners.all_pairs_cflr_tool_runner import IncompatibleCflrToolError
from cfpq_eval.runners.all_pairs_cflr_tool_runner_facade import run_appropriate_all_pairs_cflr_tool

DISPLAY_STD_THRESHOLD = 0.1

# see `man timeout`
TIMEOUT_EXIT_CODE = 124


def is_enough_data_collected(result_file_path: Path, rounds: int):
    try:
        with open(result_file_path, 'r', encoding="utf-8") as file:
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
        with open(result_file_path, 'w', newline='', encoding="utf-8") as csvfile:
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

        with open(result_file_path, 'a', newline='', encoding="utf-8") as csvfile:
            print(f"   {s_edges} {ram_kb} {time_sec}")
            writer = csv.writer(csvfile)
            writer.writerow([
                algo_name,
                os.path.basename(graph_base_name),
                os.path.basename(grammar_base_name),
                s_edges,
                ram_kb,
                time_sec
            ])


def round_to_significant_digits(x: float, digits: int = 2) -> float:
    if x == 0:
        return x
    return round(x, max(0, -int(floor(log10(abs(x)))) + digits - 1))


def reduce_result_file_to_one_row(result_file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(result_file_path)

    if len(df) == 0:
        return df

    df['ram_gb'] = df['ram_kb'].apply(
        lambda x: x / 10 ** 6 if isinstance(x, (int, float)) else x
    )
    assert df['algo'].nunique() <= 1
    assert df['graph'].nunique() <= 1
    assert df['grammar'].nunique() <= 1
    if df['s_edges'].isin(['OOM', 'OOT', '-']).any():
        # leave only one entry
        df = df[df['s_edges'].isin(['OOM', 'OOT', '-'])].head(1)
    else:
        unique_s_edges = df['s_edges'].unique()
        if len(unique_s_edges) > 1:
            warnings.warn(f"Inconsistent 's_edges' values {unique_s_edges} "
                          f"found in {result_file_path}. Using first 's_edges' value.")

        ram_gb_mean = df['ram_gb'].mean()
        time_sec_mean = df['time_sec'].mean()

        # sample standard deviation
        ram_gb_std = df['ram_gb'].std(ddof=1) if len(df) > 1 else -1
        time_sec_std = df['time_sec'].std(ddof=1) if len(df) > 1 else -1

        df = pd.DataFrame({
            'algo': [df['algo'].iloc[0]],
            'graph': [df['graph'].iloc[0]],
            'grammar': [df['grammar'].iloc[0]],
            's_edges': [df['s_edges'].iloc[0]],
            'ram_gb': [
                round_to_significant_digits(ram_gb_mean)
                if ram_gb_std < DISPLAY_STD_THRESHOLD * ram_gb_mean
                else f"{round_to_significant_digits(ram_gb_mean)}"
                     f" ± {round_to_significant_digits(ram_gb_std)}"
            ],
            'time_sec': [
                # Graspan reports analysis time in whole seconds, so it may report 0
                (round_to_significant_digits(time_sec_mean) if time_sec_mean != 0 else "< 1")
                if time_sec_std < DISPLAY_STD_THRESHOLD * time_sec_mean
                else f"{round_to_significant_digits(time_sec_mean)}"
                     f" ± {round_to_significant_digits(time_sec_std)}"
            ]
        })
    return df


def pprint_df(df: pd.DataFrame, title: str):
    df_string = df.to_markdown(maxheadercolwidths=12, maxcolwidths=12)
    width = max(len(line) for line in df_string.splitlines())
    print(title.center(width, "="))
    print(df_string)
    print("=" * width)


def min_numeric(series: pd.Series) -> float:
    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    return float('inf') if numeric_series.empty else numeric_series.min()


def display_results_for_grammar(df: pd.DataFrame, grammar: str):
    df = df[df['grammar'] == grammar].copy()
    df['algo'] = df['algo'].apply(lambda algo: algo.lower())
    df.drop(columns=['grammar'], inplace=True)

    df['graph'] = pd.Categorical(df['graph'], sorted(
        df['graph'].unique(),
        key=lambda graph: min_numeric(df[df['graph'] == graph]['time_sec'])
    ))

    s_edges_df = df.pivot(index='graph', columns='algo', values='s_edges').sort_index()
    s_edges_df.columns = [
        f'{col} (HAS KNOWN BUGS)'
        if "pocr" in col.lower()
        else col
        for col in s_edges_df.columns
    ]
    pprint_df(
        s_edges_df,
        title=f" #ANSWER (grammar '{grammar}') ",
    )

    print()
    ram_df = df.pivot(index='graph', columns='algo', values='ram_gb').sort_index()
    pprint_df(
        ram_df,
        title=f" RAM, GB (grammar '{grammar}') "
    )
    print()
    time_df = df.pivot(index='graph', columns='algo', values='time_sec').sort_index()
    pprint_df(
        time_df,
        title=f" TIME, SEC (grammar '{grammar}') "
    )
    print()
    print()


def display_results(result_files_paths: List[Path]) -> None:
    print()
    print("RESULTS:")
    print(f"Sample std is shown when it's over {DISPLAY_STD_THRESHOLD * 100}% of the mean.")
    print()

    df = pd.concat(
        [
            reduce_result_file_to_one_row(result_file_path)
            for result_file_path in result_files_paths
        ],
        ignore_index=True
    )
    df['algo'] = pd.Categorical(df['algo'], categories=df['algo'].unique())
    with pd.option_context(
            'display.max_rows', None,
            'display.max_columns', None
    ):
        for grammar in df['grammar'].unique():
            display_results_for_grammar(df, grammar)
    print(f"Sample std is shown when it's over {DISPLAY_STD_THRESHOLD * 100}% of the mean.")


def eval_all_pairs_cflr(
        algo_config: Path,
        data_config: Path,
        result_path: Path,
        rounds: Optional[int],
        timeout_sec: Optional[int],
):
    result_files_paths = []
    with open(algo_config, mode='r', encoding="utf-8") as algo_file:
        algo_reader = csv.DictReader(algo_file)
        for algo_row in algo_reader:
            algo_name = algo_row['algo_name']
            print(f"Running algorithm: {algo_name}")
            algo_settings = algo_row['algo_settings']
            algo_result_path = os.path.join(result_path, algo_name)
            if not os.path.exists(algo_result_path):
                os.makedirs(algo_result_path)

            with open(data_config, mode='r', encoding="utf-8") as data_file:
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
                    result_files_paths.append(result_file_path)
    display_results(result_files_paths)


def main(raw_args: List[str]):
    parser = argparse.ArgumentParser(
        description='Evaluates all vertex pairs '
                    'Context-Free Language Reachability (CFL-R) algorithms.'
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


if __name__ == "__main__":  # pragma: no cover
    main(raw_args=sys.argv[1:])  # pragma: no cover
