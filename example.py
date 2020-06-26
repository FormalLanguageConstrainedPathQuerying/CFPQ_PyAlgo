from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.time_profiler import SimpleTimer
from src.algo.matrix_base import matrix_base_algo

g = LabelGraph.from_txt('deps/CFPQ_Data/data/WorstCase/Matrices/worstcase_128.txt')
gr = CnfGrammar.from_cnf('deps/CFPQ_Data/data/WorstCase/Grammars/Brackets.cnf')

with SimpleTimer():
    m = matrix_base_algo(g, gr)
