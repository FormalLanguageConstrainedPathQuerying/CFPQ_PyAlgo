## CFPQ_PyAlgo

The CFPQ_PyAlgo is a repository for developing, testing and evaluating solvers for
Formal-Language-Constrained Path Problems, such as Context-Free Path Queries (CFPQ) and Regular Path Queries (RPQ).

All algorithms are based on the [GraphBLAS](http://graphblas.org) framework that allows to represent graphs as matrices
and work with them in terms of linear algebra.

## Installation

For the installation instructions, refer to [docs/install.md](docs/install.md).  

## CLI
CFPQ_PyAlgo provides a command line interface for running 
all-pairs CFPQ solver with relation query semantics.

For more details, refer to [docs/cli.md](docs/cli.md).  

## Evaluation

CFPQ_PyAlgo provides scripts for evaluating performance 
of various CFPQ solvers (including third-party ones).

For more details, refer to [docs/eval.md](docs/eval.md).

## Project structure
The global project structure is the following.

```
├── cfpq_algo - FastMatrixCFPQ and MatrixCFPQ algorithms implementations
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
