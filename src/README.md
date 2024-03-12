# LEGACY WARNING

This folder contains legacy CFPQ implementations.

New optimized CFPQ implementations are being implemented in [cfpq_algo](../cfpq_algo) folder
and can be used via scripts in [cfpq_cli](../cfpq_cli) folder.

<details>
<summary>Full README</summary>

## Benchmark
For legacy CFPQ benchmarks see [benchmark](../benchmark) folder.

## Usage

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

## File structure
The file structure of this folder is the following:

```
.
src
├── problems - directory where all the problems CFPQ that we know how to solve
│   ├───AllPaths
│   ├───Base
│   ├───MultipleSource
│   └───SinglePath
├── grammar - directory for all grammar formats representation and its loading  
├── graph - directory for all graph formats representation and its loading
└── utils - directory for other useful classes and methods
```

</details>