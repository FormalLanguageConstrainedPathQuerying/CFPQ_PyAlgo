from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo
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
