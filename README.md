[![CircleCI](https://circleci.com/gh/JetBrains-Research/CFPQ_PyAlgo/tree/master.svg?style=svg)](https://circleci.com/gh/JetBrains-Research/CFPQ_PyAlgo/tree/master)

# CFPQ_PyAlgo
The CFPQ_PyAlgo is a repository for developing, testing and benchmarking algorithms that solve Formal-Language-Constrained Path Problems, such as Context-Free Path Queries and Regular Path Queries. All algorithms are based on the [GraphBLAS](http://graphblas.org/index.php?title=Graph_BLAS_Forum) framework that allows you to represent graphs as matrices and work with them in terms of linear algebra. For convenience, all the code is written in Python using [pygraphblas](https://github.com/michelp/pygraphblas) or in C/C++ using purely [SuiteSparse](https://github.com/DrTimothyAldenDavis/SuiteSparse/tree/master/GraphBLAS) with a Python wrapper. 

# Installation
First of all you need to clone repository with its submodules:

```bash
git clone --recurse-submodules https://github.com/JetBrains-Research/CFPQ_PyAlgo.git
cd CFPQ_PyAlgo/ 
git submodule init
git submodule update
```
Then the easiest way to get started is to use Docker. An alternative, which is more correct, is to install everything directly.

## Using Docker
The first way to start is to use Docker:

```bash
# build docker image
docker build --tag <some_tag> .

# run docker container
docker run --rm -it -v ${PWD}:/CFPQ_PyAlgo <some_tag> bash
```
After it you can develop everything locally and run tests and benchmarks inside the container. Also you can use PyCharm and [configure an interpreter using Docker]( https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html).

## Direct install
The correct way is to install everything into your local python interpreter or virtual environment.

First of all you need to install [pygraphblas](https://github.com/michelp/pygraphblas) package.
```bash
pip3 install pygraphblas
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
# Benchmark
Look please [Readme](https://github.com/JetBrains-Research/CFPQ_PyAlgo/blob/master/benchmark/README.md) in *benchmark*

# Usage

Let's describe an example of using the implementation outside this environment.

For example, you want to solve a basic problem CFPQ using the matrix algorithm. To do this, you need a context-free grammar (**Gr**), as well as a graph (**G**) in the format of "triplets". 

Then the matrix algorithm can be run as follows, where *PATH_TO_GRAMMAR* --- path to file with **Gr**, *PATH_TO_GRAPH* --- path to file with **G**

```cython
from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo
from cfpq_data import cfg_from_txt
from src.graph.graph import Graph

from pathlib import Path

algo = MatrixBaseAlgo()
algo.prepare(Graph.from_txt(Path(PATH_TO_GRAPH)), cfg_from_txt(Path(PATH_TO_GRAMMAR)))
res = algo.solve()
print(res.matrix_S.nvals)
```
The given fragment displays the number of pairs of vertices between which the desired path exists.

More examples can be found in *test*

# Project structure
The global project structure is the following:

```
.
├── deps
│   └── CFPQ_Data - repository with graphs and grammars suites
├───benchmark - directory for performance measurements of implementations
├── src
│   ├── problems - directory where all the problems CFPQ that we know how to solve
│   │   ├───AllPaths
│   │   ├───Base
│   │   ├───MultipleSource
│   │   └───SinglePath
│   ├── grammar - directory for all grammar formats representation and its loading  
│   ├── graph - directory for all graph formats representation and its loading
│   └── utils - directory for other useful classes and methods
└── test
    ├───AllPaths - tests for implementations in src.problems.AllPaths
    ├───Base - tests for implementations in src.problems.Base
    ├───data - dataset for tests
    ├───MultipleSource - tests for implementations in src.problems.MultipleSource
    ├───SinglePath - tests for implementations in src.problems.SinglePath
    └───suites

```
