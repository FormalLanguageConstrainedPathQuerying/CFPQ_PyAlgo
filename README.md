## CFPQ_PyAlgo

The CFPQ_PyAlgo is a repository for developing, testing and evaluating solvers for
Formal-Language-Constrained Path Problems, such as Context-Free Path Queries and Regular Path Queries.

All algorithms are based on the [GraphBLAS](http://graphblas.org/index.php?title=Graph_BLAS_Forum) framework that allows to represent graphs as matrices
and work with them in terms of linear algebra.

## Installation
First of all you need to clone repository with its submodules:

```bash
git clone --recurse-submodules https://github.com/JetBrains-Research/CFPQ_PyAlgo.git
cd CFPQ_PyAlgo/ 
git submodule init
git submodule update
```
Then the easiest way to get started is to use Docker. An alternative is to install everything directly.

### Using Docker
The first way to start is to use Docker:

```bash
# build docker image
docker build --tag cfpq_py_algo .

# run docker container
docker run --rm -it -v ${PWD}:/CFPQ_PyAlgo cfpq_py_algo bash
```
After it, you can develop everything locally and run tests and benchmarks inside the container. 
Also, you can use PyCharm Professional and [configure an interpreter using Docker](https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html).

### Direct install
The other way is to install everything into your local Python 3.9 interpreter or virtual environment.

First of all you need to install [pygraphblas](https://github.com/michelp/pygraphblas) package.
```bash
pip3 install pygraphblas==5.1.8.0
```
Secondly you need to install cfpq_data_devtools package and other requirements:

```bash
cd deps/CFPQ_Data
pip3 install -r requirements.txt
python3 setup.py install --user

cd ../../
pip3 install -r requirements.txt
```
To check if the installation was successful you can run simple tests
```bash
python3 -m pytest test -v -m "CI"
```

## CLI
CFPQ_Algo provides a command line interface for running 
all-pairs CFPQ solver with relation query semantics.

See [cfpq_cli/README](cfpq_cli/README.md) for more details.

## Evaluation

CFPQ_PyAlgo provides scripts for performing evaluating performance 
of various CFPQ solvers (icluding third-party ones).

See [cfpq_eval/README](cfpq_eval/README.md) for more details.

## Project structure
The global project structure is the following:

```
├── cfpq_algo - new optimized CFPQ algorithm implementations
├── cfpq_cli - scripts for running CFPQ algorithms
├── cfpq_eval - scripts for evaluating performance of various CFPQ solvers (icluding third-party ones)
├── cfpq_matrix - matrix wrappers that improve performance of operations with matrices
├── cfpq_model - graph & grammar representations
├── deps
│   └── CFPQ_Data - repository with graphs and grammars suites
├── benchmark - directory for performance measurements of legacy CFPQ implementations
├── src - legacy CFPQ implementations
└── test - tests
```
