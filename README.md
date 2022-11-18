# CFPQ_PyAlgo

## Install

```shell
pip install -r requirements.txt
```

## Examples

### All-Pairs CFL-reachability

```python
import cfpq_data
import networkx as nx
from pyformlang.cfg import CFG

import cfpq_pyalgo.pygraphblas as algo

graph_path = cfpq_data.download("skos")
graph: nx.MultiDiGraph = cfpq_data.graph_from_csv(graph_path)

grammar = CFG.from_text(
    "S -> S subClassOf | subClassOf"
)

pairs_by_matrix_algo = algo.matrix_all_pairs_reachability(graph, grammar)  # [(79, 35)]
pairs_by_tensor_algo = algo.tensor_all_pairs_reachability(graph, grammar)  # [(79, 35)]
```

#### With edge reversal

```python
import cfpq_data
import networkx as nx
from pyformlang.cfg import CFG

import cfpq_pyalgo.pygraphblas as algo

graph_path = cfpq_data.download("skos")
graph: nx.MultiDiGraph = cfpq_data.graph_from_csv(graph_path)

reversed_edges = [
    (v, u, {"label": edge_data["label"] + "_r"})
    for u, v, edge_data in graph.edges(data=True)
]
graph.add_edges_from(reversed_edges)

grammar = CFG.from_text(
    "S -> subClassOf_r S subClassOf | subClassOf_r subClassOf"
)

pairs = algo.matrix_all_pairs_reachability(graph, grammar)  # [(35, 35)]
```

### BooleanMatrixGraph

```python
import cfpq_data

import cfpq_pyalgo.pygraphblas as algo

skos_path = cfpq_data.download("skos")
skos = cfpq_data.graph_from_csv(skos_path)

bmg = algo.bmg_from_nx_graph(skos)

```

### WCNF

```python
import cfpq_pyalgo.pygraphblas as algo

grammar = algo.WCNF.from_text(
    "S -> subClassOf_r S subClassOf | subClassOf_r subClassOf"
)
```

### BooleanMatrixRsm

```python
from pyformlang.rsa import RecursiveAutomaton as RSA

import cfpq_pyalgo.pygraphblas as algo

rsm = algo.BooleanMatrixRsm.from_rsa(RSA.from_text(
    "S -> subClassOf_r S subClassOf | subClassOf_r subClassOf"
))
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
