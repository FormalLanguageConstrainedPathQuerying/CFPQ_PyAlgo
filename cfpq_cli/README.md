# CFPQ_CLI

The `cfpq_cli` module provides a Command Line Interface (CLI) for solving
Context-Free Language Reachability (CFL-r) problem for all vertex pairs 
in a graph with respect to a specified context-free grammar.

## Getting Started

Ensure the CFPQ_PyAlgo project is properly set up on your system before using the CLI.
Setup instructions are available in the project's main [README](../README.md).

## Usage

### Running the Script

For detailed information on script options, execute the following command:

```bash
cd .. # Should be run from CFPQ_PyAlgo project root directory
python3 -m cfpq_cli.run_all_pairs_cflr --help
```

The basic command usage is as follows:

```
python3 -m cfpq_cli.run_all_pairs_cflr [OPTIONS] ALGORITHM GRAPH GRAMMAR
```

- `ALGORITHM` selects the algorithm. The available options are `IncrementalAllPairsCFLReachabilityMatrix` and `NonIncrementalAllPairsCFLReachabilityMatrix`.
- `GRAPH` specifies the path to the graph file.
- `GRAMMAR` indicates the path to the grammar file.

#### Optional Arguments

- `--time-limit TIME_LIMIT` sets the maximum execution time in seconds.
- `--out OUT` specifies the output file for saving vertex pairs.
- `--disable-optimize-block-matrix` disables the optimization of block matrices.
- `--disable-optimize-empty` disables the optimization for empty matrices.
- `--disable-lazy-add` disables lazy addition optimization.
- `--disable-optimize-format` disables optimization of matrix formats.

### Example

To solve the CFL-R problem using an incremental algorithm with a 60-second time limit for 
[indexed_tree.g](../test/pocr_data/indexed_an_bn/indexed_tree.g) and 
[an_bn_indexed.cnf](../test/pocr_data/indexed_an_bn/an_bn_indexed.cnf) and get results in 
[results.txt](../results.txt) execute:

```bash
cd .. # Should be run from CFPQ_PyAlgo project root directory
python3 -m cfpq_cli.run_all_pairs_cflr \
    IncrementalAllPairsCFLReachabilityMatrix \
    test/pocr_data/indexed_an_bn/indexed_tree.g \
    test/pocr_data/indexed_an_bn/an_bn_indexed.cnf \
    --time-limit 60 \
    --out results.txt
```

### Grammar Format

The grammar file should be formatted with each production rule on a separate line, adhering to the following schema:

```
<LEFT_SYMBOL>	[RIGHT_SYMBOL_1]	[RIGHT_SYMBOL_2]
```

- `<LEFT_SYMBOL>`: the symbol on the left-hand side of a production rule.
- `<RIGHT_SYMBOL_1>` and `<RIGHT_SYMBOL_2>`: the symbols on the right-hand side of the production rule, each of them is optional.
- The symbols must be separated by whitespace.
- The last two line specify the start symbol in the format 
  ```
  Count:
  <START_SYMBOL>
  ```

#### Example
```
S	AS_i	b_i
AS_i	a_i	S
S	c

Count:
S
```

### Graph Format

The graph file should represent edges using the format:

```
<EDGE_SOURCE>	<EDGE_DESTINATION>	<EDGE_LABEL>	[LABEL_INDEX]
```

- `<EDGE_SOURCE>` and `<EDGE_DESTINATION>`: specify the source and destination nodes of an edge.
- `<EDGE_LABEL>`: the label associated with the edge.
- `[LABEL_INDEX]`: an optional index for labels with subscripts, indicating the subscript value.
- The symbols must be separated by whitespace
- Labels with subscripts must end with "\_i". For example, an edge $1 \xrightarrow{x_10} 2$ is denoted by `1	2	x_i	10`.

#### Example
```
1	2	a_i	1
2	3	b_i	1
2	4	b_i	2
1	5	c
```
