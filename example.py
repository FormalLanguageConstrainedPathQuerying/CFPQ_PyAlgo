from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.time_profiler import SimpleTimer
from src.algo.matrix_base import matrix_base_algo
from src.algo.tensor import tensor_algo
from src.grammar.rsa import RecursiveAutomaton

from pygraphblas import *

graph = LabelGraph.from_txt('src/grammar/test/RSA/1000')
grammar = RecursiveAutomaton()
grammar.from_file('src/grammar/test/RSA/ex2')


with SimpleTimer():
    m = tensor_algo(graph, grammar)
    print(m)
