## CFPQ Evaluator

This document explains how to use `CFPQ_eval` to evaluate the performance of various Context-Free Path Querying (CFPQ)
solvers, including both the `CFPQ_PyAlgo` solver and third-party tools.

To install the `CFPQ_eval` tool, refer to [eval_install.md](eval_install.md).  
For our evaluation results, refer to [main project README](../README.md#evaluation).

## Running the Tool

For detailed information on the evaluator options, execute the following command.

```bash
# Ensure we're in the project root directory
cd $(git rev-parse --show-toplevel)

python3 -m cfpq_eval.eval_all_pairs_cflr --help
```

The basic command usage is as follows.
Note that this command should be run in [the cfpq/py_algo_eval Docker container](eval_install.md).

```
python3 -m cfpq_eval.eval_all_pairs_cflr algo_config.csv data_config.csv results_path [--rounds ROUNDS] [--timeout TIMEOUT]
```

- `algo_config.csv` specifies algorithm configurations (e.g. `configs/algo/fast_matrix.csv`);
- `data_config.csv` specifies the dataset (e.g. `configs/data/small_examples.csv`);
- `results_path` specifies the path for saving raw results;
- `--rounds` specifies the number of reruns (default is 1);
- `--timeout` specifies the maximum number of seconds a single CFPQ tool invocation can take (optional).

## Configuration Files

### Premade Configurations

The `CFPQ_eval` [Docker image](https://hub.docker.com/r/cfpq/py_algo_eval) includes premade configurations located in the `/py_algo/configs` folder.

### Algorithm Configuration

The `algo_config.csv` configuration should list algorithms and their settings.

Supported algorithms:

- [`IncrementalAllPairsCFLReachabilityMatrix`](cli.md)
- [`NonIncrementalAllPairsCFLReachabilityMatrix`](cli.md)
- [`pocr`](https://github.com/kisslune/POCR)
- [`pearl`](https://figshare.com/articles/dataset/ASE_2023_artifact/23702271)
- [`graspan`](https://github.com/Graspan/Graspan-C)
- [`gigascale`](https://bitbucket.org/jensdietrich/gigascale-pointsto-oopsla2015/src)
- [`kotgll`](https://github.com/vadyushkins/kotgll)
- [`legacy_matrix`](../src/README.md)

For first two algorithms, options described in [cli.md](cli.md)
can be used to configure optimizations.

Here's an algorithm configuration example:
```
algo_name,algo_settings
"Matrix (some optimizations disabled)",IncrementalAllPairsCFLReachabilityMatrix --disable-optimize-empty --disable-lazy-add
"pocr",pocr
```

### Data Configuration

The `data_config.csv` configuration pairs graph and grammar files.
The referenced files should be in the format described in [cli.md](cli.md).
The paths must be relative to the `CFPQ_PyAlgo` root directory.

Here's a data configuration example:
```
graph_path,grammar_path
data/graphs/aa/leela.g,data/grammars/aa.cnf
data/graphs/java/eclipse.g,data/grammars/java_points_to.cnf
```

## Interpreting Results

During evaluation, raw data is printed to `stdout` and saved to the folder specified by `results_path`.

After the evaluation, summary tables, including mean execution time,
memory usage, and output size, will be printed to `stdout`.

Here's an example of a mean execution time summary table:
```
==================================== TIME, SEC (grammar 'c_alias') ====================================
| graph    | fast matrix   | fast matrix   | pearl   | pocr      | kotgll   | gigascale   | graspan   |
|          | cfpq          | cfpq (no      |         |           |          |             |           |
|          |               | grammar       |         |           |          |             |           |
|          |               | rewrite)      |         |           |          |             |           |
|:---------|:--------------|:--------------|:--------|:----------|:---------|:------------|:----------|
| init     | 1.2 ± 3%      | 2.9           | -       | 85        | 23 ± 6%  | -           | 16 ± 14%  |
| mm       | 1.3 ± 2%      | 3.1           | -       | 89 ± 1%   | 25 ± 3%  | -           | 16 ± 5%   |
| block    | 1.7 ± 2%      | 4.1           | -       | 123       | 34 ± 3%  | -           | 21 ± 2%   |
| ipc      | 1.7 ± 4%      | 4.0           | -       | 121 ± 1%  | 34 ± 1%  | -           | 21 ± 3%   |
| lib      | 1.7 ± 2%      | 4.0           | -       | 123 ± 1%  | 34 ± 1%  | -           | 21 ± 3%   |
| arch     | 1.7 ± 3%      | 4.1           | -       | 123 ± 1%  | 34 ± 5%  | -           | 22 ± 10%  |
| crypto   | 1.7 ± 3%      | 4.2           | -       | 125 ± 1%  | 34 ± 2%  | -           | 22 ± 8%   |
| security | 1.8 ± 4%      | 4.4           | -       | 129 ± 1%  | 35 ± 5%  | -           | 22 ± 5%   |
| sound    | 2.0 ± 2%      | 5.0           | -       | 140 ± 1%  | 38 ± 5%  | -           | 24 ± 11%  |
| fs       | 2.5 ± 2%      | 6.9           | -       | 230 ± 1%  | 53 ± 1%  | -           | 34 ± 3%   |
| net      | 2.6 ± 3%      | 7.4           | -       | 221 ± 1%  | 52 ± 1%  | -           | 35 ± 2%   |
| drivers  | 3.9 ± 2%      | 12 ± 1%       | -       | 755 ± 1%  | 92 ± 3%  | -           | 69 ± 3%   |
| kernel   | 6.1 ± 2%      | 13            | -       | 387 ± 1%  | 118 ± 2% | -           | 69 ± 3%   |
| apache   | 6.5 ± 1%      | 26 ± 1%       | -       | OOT       | OOM      | -           | 601 ± 2%  |
| postgre  | 10 ± 1%       | 36 ± 1%       | -       | 5398 ± 1% | OOM      | -           | 427 ± 4%  |
=======================================================================================================
```

## Custom Tools Integration

Custom CFPQ solvers can be evaluated by implementing the `AllPairsCflrToolRunner` interface
and updating the `run_appropriate_all_pairs_cflr_tool()` function.
