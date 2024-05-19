import sys
from pathlib import Path
from time import time
from typing import List

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.graph import Graph
from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo


# Minimalistic CLI needed for integration with cfpq_eval,
# not intended to be used by consumers
def main(raw_args: List[str]):
    graph_path = raw_args[0]
    grammar_path = raw_args[1]
    algo = MatrixBaseAlgo()

    algo.graph = Graph.from_txt(Path(graph_path))
    algo.graph.load_bool_graph()
    algo.grammar = CnfGrammar.from_cnf(grammar_path)

    start = time()
    res = algo.solve()
    finish = time()
    print(f"AnalysisTime\t{finish - start}")
    print(f"#SEdges\t{res.matrix_S.nvals}")


if __name__ == '__main__':
    main(raw_args=sys.argv[1:])
