# How to start
First, create a directory for the dataset. It should have two subdirectories for graphs (Graphs) and grammars (Grammars). In the second step, select an algorithm for benchmarking. Then run the command: 
```
python3 start_benchmark.py -algo ALGO -data_dir DATA_DIR
```
You can also set the number of rounds for measurements (-round), a config file (-config) in the "graph grammar" format to indicate only certain data for measurements from a directory (DATA_DIR), indicate additionally measure the extraction of paths (-with_paths), and also specify a directory for uploading the results (-result_dir).