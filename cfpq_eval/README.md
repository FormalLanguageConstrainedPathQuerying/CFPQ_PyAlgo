# CFPQ Evaluation

The `cfpq_eval` module evaluates performance of various CFPQ solvers,
integrating with both CFPQ_PyAlgo itself and third-party tools.

## Setting up the environment

Build and run a Docker container for evaluation using [Dockerfile-all-tools](../Dockerfile-all-tools).

Build Docker image:
```bash
cd .. # Should be run from CFPQ_PyAlgo project root directory

# Load base image
wget -O pearl.tar.gz https://figshare.com/ndownloader/files/42214812
docker load --input pearl.tar.gz
rm pearl.tar.gz

# Build eval image
docker build -f Dockerfile-all-tools -t cfpq/py_algo_eval .
```

Run Docker container:
```bash
docker run -it cfpq/py_algo_eval bash
```

## Running the Script

For detailed information on evaluation script options, execute the following command:

```bash
cd .. # Should be run from CFPQ_PyAlgo project root directory
python3 -m cfpq_eval.eval_all_pairs_cflr --help
```

The basic command usage is as follows:

```
# Should be run in cfpq_eval Docker container
python3 -m cfpq_eval.eval_all_pairs_cflr algo_config.csv data_config.csv results_path [--rounds ROUNDS] [--timeout TIMEOUT]
```

- `algo_config.csv` specifies algorithm configurations (e.g. `configs/algo/fast_matrix_cfpq.csv`).
- `data_config.csv` specifies the dataset (e.g. `configs/data/small_examples.csv`).
- `results_path` specifies path for saving raw results.
- `--rounds` sets run times per config (default is 1).
- `--timeout` limits each configuration's execution time in seconds (optional).

## Configuration Files

### Premade Configurations

The CFPQ_eval Docker image includes premade configurations located in the `/py_algo/configs` folder.
### Algorithm Configuration

The `algo_config.csv` outlines algorithms and settings. Supported algorithms:

- `IncrementalAllPairsCFLReachabilityMatrix`
- `NonIncrementalAllPairsCFLReachabilityMatrix`
- `pocr`
- `pearl`
- `graspan`
- `gigascale`

For Matrix-based algorithms options described in [cfpq_cli/README](../cfpq_cli/README.md)
can be used to alter the behaviour.

#### Example

```
algo_name,algo_settings
"Matrix (some optimizations disabled)",IncrementalAllPairsCFLReachabilityMatrix --disable-optimize-empty --disable-lazy-add
"pocr",pocr
```

### Data Configuration

The `data_config.csv` pairs graph and grammar files, 
referenced files should be in format described in [cfpq_cli/README](../cfpq_cli/README.md).

#### Example

```
graph_path,grammar_path
data/graphs/aa/leela.g,data/grammars/aa.cnf
data/graphs/java/eclipse.g,data/grammars/java_points_to.cnf
```

## Interpreting Results

Raw data is saved to `results_path`, while quick summary including mean execution time,
memory usage, and output size are rendered in standard output stream.

## Custom Tools Integration

Custom CFPQ solvers can be evaluated by implementing `AllPairsCflrToolRunner` interface
and updating `run_appropriate_all_pairs_cflr_tool()` function.
