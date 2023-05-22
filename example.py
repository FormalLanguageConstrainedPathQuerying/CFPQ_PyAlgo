from src.grammar.one_term_rsa import TemplateRSA
from src.graph.one_terminal_graph import OneTerminalGraph
from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo
from src.problems.Base.algo.tensor.one_terminal_tensor import OneTerminalTensorAlgo
from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSBruteAlgo, MatrixMSOptAlgo
from src.problems.MultipleSource.algo.tensor_ms.tensor_ms import TensorMSAlgo
from src.problems.AllPaths.algo.tensor.tensor import TensorSimpleAlgo, TensorDynamicAlgo
from src.problems.SinglePath.algo.matrix_single_path.matrix_single_path_index import MatrixSingleAlgo
from src.problems.SinglePath.algo.matrix_shortest_path.matrix_shortest_path_index import MatrixShortestAlgo

from src.graph.graph import Graph
from cfpq_data import cfg_from_txt

from src.problems.utils import ResultAlgo

from pathlib import Path

CASE = Path("test/data/binary_tree/")

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = MatrixBaseAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve()
print(f'MatrixBaseAlgo: {res.matrix_S.nvals}')

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = TensorSimpleAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve()
print(f'TensorSimpleAlgo: {res.matrix_S.nvals}')

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = TensorDynamicAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve()
print(f'TensorDynamicAlgo: {res.matrix_S.nvals}')

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = MatrixSingleAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve()
print(f'MatrixSingleAlgo: {res.matrix_S.nvals}')

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = MatrixShortestAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve()
print(f'MatrixShortestAlgo: {res.matrix_S.nvals}')

graph = Graph.from_txt(CASE.joinpath("../single_vs_shortest/Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("../single_vs_shortest/Grammars/g.cfg"))
algo = MatrixShortestAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve()
print(f'MatrixShortestAlgo: {res.matrix_S.nvals}')
print(f'MatrixShortestAlgo shortest path 0 - 7: {algo.getPath(0, 7, "S")}')

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = MatrixMSBruteAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve([0])[0]
print(f'MatrixMSBruteAlgo from 0: {res.matrix_S.nvals}')

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = MatrixMSOptAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve([0])[0]
print(f'MatrixMSOptAlgo from 0: {res.matrix_S.nvals}')

graph = Graph.from_txt(CASE.joinpath("Graphs/graph_1.txt"))
grammar = cfg_from_txt(CASE.joinpath("Grammars/g.cfg"))
algo = TensorMSAlgo()
algo.prepare(graph, grammar)
res:ResultAlgo = algo.solve([0])[0]
print(f'TensorMSAlgo from 0: {res.matrix_S.nvals}')


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


CASE = Path("test/data/template_rsa")
template_rsa = TemplateRSA.from_file(CASE.joinpath("Grammars/java_pt.rsa"))
graph = OneTerminalGraph.from_file(
    CASE.joinpath("Graphs/java_example.csv"),
    template_rsa,
    process_multiedge_java
)
algo = OneTerminalTensorAlgo()
res: ResultAlgo = algo.solve("PointsTo", graph)
print(f'TensorOneTerminalAlgo: {res.matrix_S.nvals}')