import argparse
import os
import sys
from time import time
from typing import Optional, List

import graphblas
from graphblas.core.matrix import Matrix
from graphblas.core.dtypes import BOOL

from cfpq_algo.all_pairs.matrix.incremental_all_pairs_cfl_reachability_algo import \
    IncrementalAllPairsCFLReachabilityMatrixAlgo
from cfpq_algo.setting.matrix_optimizer_setting import OptimizeEmptyMatrixSetting, OptimizeFormatMatrixSetting, \
    LazyAddMatrixSetting
from cfpq_cli.time_limit import time_limit, TimeoutException
from cfpq_decomposer.high_performance_decomposer import HighPerformanceDecomposer
from cfpq_decomposer.prototype_decomposer import PrototypeDecomposer
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph

_CFLR_ALGO_SETTINGS = [
    OptimizeEmptyMatrixSetting(),
    LazyAddMatrixSetting(),
    OptimizeFormatMatrixSetting()
]

def decompose_all_pairs_cflr(solution: Matrix, use_prototype: bool):
    start = time()
    decomposer = PrototypeDecomposer() if use_prototype else HighPerformanceDecomposer()
    left, right = decomposer.decompose(solution)
    finish = time()
    print(f"Decomposition time\t{finish - start}")
    left_right = left.mxm(right, op=graphblas.semiring.any_pair)
    remainder_nvals = solution.nvals - left_right.new(dtype=BOOL).nvals
    print(f"Left N vals\t{left.nvals}")
    print(f"Right N vals\t{right.nvals}")
    print(f"Remainder N vals\t{remainder_nvals}")
    print(f"Compression factor\t{solution.nvals / (left.nvals + right.nvals + remainder_nvals)}")
    print(f"Is compression valid\t{left_right.new(mask=~solution.S).nvals == 0}")

def run_and_decompose_all_pairs_cflr(
        graph_path: str,
        grammar_path: str,
        out_path: Optional[str],
        time_limit_sec: int,
        use_prototype: bool,
):
    algo = IncrementalAllPairsCFLReachabilityMatrixAlgo()
    graph = LabelDecomposedGraph.read_from_pocr_graph_file(graph_path)
    grammar = CnfGrammarTemplate.read_from_pocr_cnf_file(grammar_path)
    try:
        with time_limit(time_limit_sec):
            start = time()
            res = algo.solve(
                graph=graph,
                grammar=grammar,
                settings=_CFLR_ALGO_SETTINGS
            )
            finish = time()
            print(f"AnalysisTime\t{finish - start}")
            print(f"#SEdges\t{res.nvals}")
            decompose_all_pairs_cflr(res, use_prototype)
        if out_path is not None:
            out_dir = os.path.dirname(out_path)
            if out_dir != "" and not os.path.exists(out_dir):
                os.makedirs(out_dir)
            with open(out_path, 'w', encoding="utf-8") as out_file:
                for (source, target) in res:
                    out_file.write(f"{source}\t{target}\n")

    except TimeoutException:
        print("AnalysisTime\tNaN")
        print("#SEdges\tNaN")


def main(raw_args: List[str]):
    parser = argparse.ArgumentParser(
        description="Solves the Context-Free Language Reachability (CFL-R) problem "
                    "for all vertex pairs, decomposes the solution and "
                    "calculates a compression factor.",
    )
    parser.add_argument(dest='graph',
                        help='Specifies the graph file in POCR format. The line format is: '
                             '`<EDGE_SOURCE> <EDGE_DESTINATION> <EDGE_LABEL> [LABEL_INDEX]`, '
                             'with values separated by whitespace characters. '
                             '[LABEL_INDEX] is optional. '
                             'Indexed label names should end with `_i`.')
    parser.add_argument(dest='grammar',
                        help='Specifies the grammar file in POCR format. '
                             'Non-empty lines (except the last two) denote grammar rules: '
                             'complex rules (`<NON_TERMINAL> <SYMBOL_1> <SYMBOL_2>`), '
                             'simple rules (`<NON_TERMINAL> <TERMINAL>`), '
                             'and epsilon rules (`<NON_TERMINAL>`), '
                             'with values separated by whitespace characters. '
                             'Indexed symbol names should end with `_i`. '
                             'The final two lines define the starting non-terminal as: '
                             '`Count:\\n <START_NON_TERMINAL>`.')
    parser.add_argument('--time-limit', dest='time_limit', default=None, type=int,
                        help='Sets a time limit in seconds.')
    parser.add_argument('--out', dest='out', default=None,
                        help='Specifies the output file for saving vertex pairs. '
                             'The line format is: `[START_VERTEX]\t[END_VERTEX]`. '
                             'Each line indicates a path exists from [START_VERTEX] '
                             'to [END_VERTEX], labels along which spell a word from '
                             'the specified Context-Free Language (CFL).'
                        )
    parser.add_argument('--prototype',
                        action='store_true',
                        dest='prototype',
                        help='Use PrototypeDecomposer instead of HighPerformanceDecomposer.')
    args = parser.parse_args(raw_args)
    run_and_decompose_all_pairs_cflr(
        graph_path=args.graph,
        grammar_path=args.grammar,
        time_limit_sec=args.time_limit,
        out_path=args.out,
        use_prototype=args.prototype,
    )


if __name__ == "__main__":       # pragma: no cover
    main(raw_args=sys.argv[1:])  # pragma: no cover
