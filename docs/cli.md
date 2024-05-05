## CFPQ CLI

This document explains how to use the Context-Free Path Query (CFPQ) solver 
via the command line interface (CLI).

For installation instructions, refer to [install.md](install.md).

## Running the Tool

For detailed information on the tool's options, execute the following command.

```bash
# Ensure we're in the project root directory
cd $(git rev-parse --show-toplevel)

python3 -m cfpq_cli.run_all_pairs_cflr --help
```

The basic command usage is as follows.

```
python3 -m cfpq_cli.run_all_pairs_cflr [OPTIONS] ALGORITHM GRAPH GRAMMAR
```

### Required Arguments

- `ALGORITHM` specifies the algorithm to use. The available options are `IncrementalAllPairsCFLReachabilityMatrix` and `NonIncrementalAllPairsCFLReachabilityMatrix`.
- `GRAPH` specifies the path to the [graph file](#graph-format).
- `GRAMMAR` specifies the path to the [grammar file](#grammar-format).

### Optional Arguments

- `--time-limit TIME_LIMIT` sets the maximum execution time in seconds.
- `--out OUT` specifies the output file for saving vertex pairs.
- `--disable-optimize-block-matrix` disables optimization involving block matrix operations.
- `--disable-optimize-empty` disables optimization for operations with empty matrices.
- `--disable-lazy-add` disables lazy (symbolic) addition optimization.
- `--disable-optimize-format` disables matrix format optimization.

## Example

To solve the all-pairs relation-semantics CFPQ problem using an incremental algorithm with a 60-second time limit for 
[indexed_tree.g](../test/pocr_data/indexed_an_bn/indexed_tree.g) graph and 
[an_bn_indexed.cnf](../test/pocr_data/indexed_an_bn/an_bn_indexed.cnf) grammar and save results to 
[results.txt](../results.txt) execute the following command.

```bash
# Ensure we're in the project root directory
cd $(git rev-parse --show-toplevel)

python3 -m cfpq_cli.run_all_pairs_cflr \
    IncrementalAllPairsCFLReachabilityMatrix \
    test/pocr_data/indexed_an_bn/indexed_tree.g \
    test/pocr_data/indexed_an_bn/an_bn_indexed.cnf \
    --time-limit 60 \
    --out results.txt
```

## Grammar Format

The grammar file should be formatted with each production rule on a separate line, adhering to the following schema.

```
<LEFT_SYMBOL>	[RIGHT_SYMBOL_1]	[RIGHT_SYMBOL_2]
```

- `<LEFT_SYMBOL>` is the symbol on the left-hand side of a production rule.
- `[RIGHT_SYMBOL_1]` and `[RIGHT_SYMBOL_2]` are the symbols on the right-hand side of the production rule, each of them is optional.
- Symbols must be separated by whitespace.
- The last two lines specify the start symbol in the following format.
  ```
  Count:
  <START_SYMBOL>
  ```

### Example
```
S	AS_i	b_i
AS_i	a_i	S
S	c

Count:
S
```

## Graph Format

Each line of the graph file should represent an edge, adhering to the following format. 

```
<EDGE_SOURCE>	<EDGE_DESTINATION>	<EDGE_LABEL>	[LABEL_INDEX]
```

- `<EDGE_SOURCE>` and `<EDGE_DESTINATION>` are source and destination nodes of an edge.
- `<EDGE_LABEL>` is the label associated with the edge.
- `[LABEL_INDEX]` is an optional index for labels with subscripts, indicating the subscript value.
- Symbols must be separated by whitespace
- Labels with subscripts must end with "\_i". For example, an edge $1 \xrightarrow{x_10} 2$ is denoted as `1	2	x_i	10`.

### Example
```
1	2	a_i	1
2	3	b_i	1
2	4	b_i	2
1	5	c
```
