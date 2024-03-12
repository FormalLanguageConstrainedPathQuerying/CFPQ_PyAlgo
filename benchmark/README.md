# LEGACY WARNING

This folder contains benchmarks for legacy CFPQ implementations.

New optimized CFPQ implementations are being implemented in [cfpq_algo](../cfpq_algo) folder
and can be evaluated with scripts in [cfpq_eval](../cfpq_eval) folder.

<details>
<summary>Full README</summary>

## How to start
First, create a directory for the dataset. It should have two subdirectories for graphs (Graphs) and grammars (Grammars). In the second step, select an algorithm for benchmarking. Then run the command: 
```
python3 -m benchmark.start_benchmark.py -algo ALGO -data_dir DATA_DIR
```
There are also a number of optional parameters:
+ -round --- number of rounds for measurements
+ -config --- config file in the "graph grammar" format to indicate only certain data for measurements from a directory DATA_DIR
+ -with_paths --- indicate additionally measure the extraction of paths
+ -result_dir --- specify a directory for uploading the results
+ -max_len_paths --- Limit on the length of the retrieved paths 

## Add new algorithm
To add a new implementation of the algorithm to the list of available measurements, you must:
1. Add you algorithm in *algo_impl.ALGO_PROBLEM*
2. Add you implementation in *algo_impl.ALGO_IMPL*
3. Create new or use the existing pipeline or  in *bench.benchmark*

</details>
