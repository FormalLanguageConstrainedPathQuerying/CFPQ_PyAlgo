from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.time_profiler import SimpleTimer
from src.algo.matrix_base import matrix_base_algo
from src.algo.single_source.single_source import SingleSourceAlgoBrute, SingleSourceAlgoSmart, SingleSourceAlgoOpt

g = LabelGraph.from_txt('deps/CFPQ_Data/data/WorstCase/Matrices/worstcase_128.txt')
gr = CnfGrammar.from_cnf('deps/CFPQ_Data/data/WorstCase/Grammars/Brackets.cnf')

print('matrix_base_algo:')

with SimpleTimer():
    m = matrix_base_algo(g, gr)

ss_ab = SingleSourceAlgoBrute(g, gr)
sources_vertices = range(128)

print('SingleSourceAlgoBrute:')

with SimpleTimer():
    m1 = ss_ab.solve(sources_vertices)

ss_as = SingleSourceAlgoSmart(g, gr)

sum = 0
for i in sources_vertices:
    st = SimpleTimer()
    st.tic()
    m2 = ss_as.solve([i])
    st.toc()
    sum += st.duration

print(f'SingleSourceAlgoSmart:\n{sum}')

ss_ao = SingleSourceAlgoOpt(g, gr)

sum = 0
for i in sources_vertices:
    st = SimpleTimer()
    st.tic()
    m3 = ss_ao.solve([i])
    st.toc()
    sum += st.duration

print(f'SingleSourceAlgoOpt:\n{sum}')

assert m.to_lists() == m1.to_lists(), 'Not equal!'
assert m.to_lists() == m2.to_lists(), 'Not equal!'
assert m.to_lists() == m3.to_lists(), 'Not equal!'
