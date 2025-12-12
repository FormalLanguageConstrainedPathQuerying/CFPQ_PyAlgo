import argparse
import csv
import typing
from os.path import exists
from pathlib import Path

# import cfpq_data
# from cfpq_data.grammars.readwrite.rsa import rsa_from_txt
# from cfpq_data.grammars.readwrite.cfg import cfg_from_txt
# from pyformlang.cfg import Variable

from src.grammar.one_term_rsa import TemplateRSA
from src.graph.one_terminal_graph import OneTerminalGraph
from src.problems.Base.algo.tensor.one_terminal_tensor import OneTerminalDynamicTensorAlgo
from src.problems.utils import ResultAlgo
from src.utils.useful_paths import LOCAL_CFPQ_DATA
from tqdm import tqdm
from time import time

import sys
import csv
import time
def process_multiedge_java(v_from, terminal, v_to, edges, graph_size):
    if (v_from, v_to) in edges:
        v_new = graph_size
        graph_size += 1
        if terminal.startswith("store"):
            edges[(v_from, v_new)] = terminal
            edges[(v_new, v_from)] = f'{terminal}_r'
            edges[(v_new, v_to)] = "assign"
            edges[(v_to, v_new)] = "assign_r"
        else:
            edges[(v_from, v_new)] = "assign"
            edges[(v_new, v_from)] = "assign_r"
            edges[(v_new, v_to)] = terminal
            edges[(v_to, v_new)] = f'{terminal}_r'
    elif v_from == v_to:
        v_new_1 = graph_size
        v_new_2 = graph_size + 1
        graph_size += 2
        if terminal.startswith("store"):
            edges[(v_from, v_new_1)] = terminal
            edges[(v_new_1, v_from)] = f'{terminal}_r'
            edges[(v_new_1, v_new_2)] = "assign"
            edges[(v_new_2, v_new_1)] = "assign_r"
            edges[(v_new_2, v_to)] = "assign"
            edges[(v_to, v_new_2)] = "assign_r"
        else:
            edges[(v_from, v_new_1)] = "assign"
            edges[(v_new_1, v_from)] = "assign_r"
            edges[(v_new_1, v_new_2)] = "assign"
            edges[(v_new_2, v_new_1)] = "assign_r"
            edges[(v_new_2, v_to)] = terminal
            edges[(v_to, v_new_2)] = f'{terminal}_r'
    return edges, graph_size


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <graph_path> <grammar_path> <output_path>")
    sys.exit(1)

graph_path = sys.argv[1]
grammar_path = sys.argv[2]
output_path = sys.argv[3]

start_load_time = time.time()
template_rsa = TemplateRSA.from_file(
    './msbfs_tensor_bench_rsuvorov/java_pt.rsa')
print("loaded rsa")
graph = OneTerminalGraph.from_file('./java_data/graphs/lusearch/data.csv',
        template_rsa,
        process_multiedge_java
    )
# algo = OneTerminalTensorAlgo()
print("loaded graph")
algo = OneTerminalDynamicTensorAlgo()


start_run_time = time.time()

# res: ResultAlgo = algo.solve("PointsTo", graph)
res: ResultAlgo = algo.solve("PointsTo", graph)
finish_time = time.time()

with open(output_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        start_run_time - start_load_time,
        finish_time - start_run_time,
        res.matrix_S.nvals
    ])