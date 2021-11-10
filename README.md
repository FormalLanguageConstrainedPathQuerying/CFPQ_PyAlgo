# CFPQ_PyAlgo

## Install

```shell
pip install -r requirements.txt
```

## Examples

### BooleanMatrixGraph

```python
import networkx as nx
import cfpq_pyalgo.pygraphblas as algo
import cfpq_data

bzip_path = cfpq_data.download("bzip")
bzip = cfpq_data.graph_from_csv(bzip_path)

bmg = algo.BooleanMatrixGraph.from_nx_graph(bzip)
```

### WCNF

```python
from pyformlang.cfg import CFG
import cfpq_pyalgo.pygraphblas as algo

cfg = CFG.from_text("S -> a S b S | a b")

wcnf = algo.WCNF(cfg)
```

## pre-commit

### Install

```shell
pip install pre-commit==2.15.0
pre-commit install
```

### Run

```shell
pre-commit run --all-files --color always --verbose
```
