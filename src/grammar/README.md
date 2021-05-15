# Presentation formats of grammars
Consider presentation formats grammar CNF and RSA

# Format of RSA

Let the CF grammar be given:
```
S -> a S b | a b
```
Thus RSA for this grammar should be represented in the file as follows:
```
3
1
4
a
1
0 1
S
1
1 2
b
2
1 3
2 3
S
1
0 3
```
Where
* First line is number of different labels on edges
* Second line is number of nonterminals
* Third line is size of adjacency matrix size
* Then there are triples of lines, the number of which is equal to the number on the first line in format
    ```
    label
    number of edges with this label
    two states with this label
    ```
* This is followed by information about the start and finish state of the automaton in format
    ```
    nonterminal
    number of start and finish states
    two states: start and finish for this nonterminal
    ```
# Format for grammar CNF

This format is the same as the format in *deps/CFPQ_Data*