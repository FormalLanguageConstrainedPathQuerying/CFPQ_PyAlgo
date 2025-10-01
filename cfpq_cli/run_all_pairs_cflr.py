import argparse
import os
import sys
from time import time
from typing import Optional, List

from cfpq_algo.all_pairs.all_cfl_pairs_reachability_impls import \
    ALL_PAIRS_CFL_REACHABILITY_ALGO_NAMES, \
    get_all_pairs_cfl_reachability_algo
from cfpq_algo.setting.algo_setting import AlgoSetting
from cfpq_algo.setting.algo_settings_manager import AlgoSettingsManager
from cfpq_algo.setting.preprocessor_setting import preprocess_graph_and_grammar
from cfpq_cli.time_limit import time_limit, TimeoutException
from cfpq_model.cnf_grammar_template import CnfGrammarTemplate
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph
from cfpq_add_context.add_contexts import add_context, normalize
from cfpq_add_context.utils import verify

import graphblas

def run_all_pairs_cflr(
        algo_name: str,
        graph_path: str,
        grammar_path: str,
        time_limit_sec: Optional[int],
        out_path: Optional[str],
        settings: List[AlgoSetting],
        add_contexts: bool = False,
        expected_path: str = "",
        max_num_of_contexts = 30,
        trace_graphblas = False,
        depth=1,
):
    if trace_graphblas: graphblas.ss.burble.enable()
    total_start = time()
    algo = get_all_pairs_cfl_reachability_algo(algo_name)
    if add_contexts:
        graph,initial_graph_nvertices = add_context(graph_path, max_num_of_contexts,depth)
    else:
        graph = LabelDecomposedGraph.read_from_pocr_graph_file(graph_path)
    grammar = CnfGrammarTemplate.read_from_pocr_cnf_file(grammar_path)
    graph, grammar = preprocess_graph_and_grammar(graph, grammar, settings)
    try:
        with time_limit(time_limit_sec):
            start = time()
            res = algo.solve(graph=graph, grammar=grammar, settings=settings)
            if add_contexts:
                res = normalize(res, initial_graph_nvertices)
            if (len(expected_path) > 0)   and not (verify(res, expected_path)):
                print("!!! Incorrect result !!!")
            finish = time()
            #print("result: ", res)
            print(f"AnalysisTime\t{finish - start}")
            print(f"#SEdges\t{res.nvals}")
            if out_path is not None:
                out_dir = os.path.dirname(out_path)
                if out_dir != "" and not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                with open(out_path, 'w', encoding="utf-8") as out_file:
                    for (source, target) in res:
                        out_file.write(f"{source}\t{target}\n")
            print ("Graph name: ", graph_path)
            print("Total execution time = ", time() - total_start)
    except TimeoutException:
        print("AnalysisTime\tNaN")
        print("#SEdges\tNaN")


def main(raw_args: List[str]):
    parser = argparse.ArgumentParser(
        description="Solves the Context-Free Language Reachability (CFL-R) problem "
                    "for all vertex pairs.",
    )
    parser.add_argument(dest='algo', choices=ALL_PAIRS_CFL_REACHABILITY_ALGO_NAMES,
                        help='Specifies the algorithm to use.')
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
    parser.add_argument('--max-num-of-contexts', dest='max_num_of_contexts', default=30, type=int,
                        help='Sets a maximal number of contexts.')
    parser.add_argument('--depth-of-contexts', dest='depth', default=1, type=int,
                        help='Sets a maximal depth of contexts.')
    parser.add_argument('--out', dest='out', default=None,
                        help='Specifies the output file for saving vertex pairs. '
                             'The line format is: `[START_VERTEX]\t[END_VERTEX]`. '
                             'Each line indicates a path exists from [START_VERTEX] '
                             'to [END_VERTEX], labels along which spell a word from '
                             'the specified Context-Free Language (CFL).'
                        )
    parser.add_argument('--add_contexts', dest='add_contexts', default=False,
                        help='Specifies whether approximation of context sensitivity should be added.'
                        )
    parser.add_argument('--trace-graphblas', dest='trace_graphblas', default=False,
                        help='Turn GraphBLAS burble on.'
                        )                        
    parser.add_argument('--expected_path', dest='expected_path', default="",
                        help='If specified, it will be checked wether solver\'s result is overapproximation of represented in the file.'
                        )
    settings_manager = AlgoSettingsManager()
    settings_manager.add_args(parser)
    args = parser.parse_args(raw_args)
    run_all_pairs_cflr(
        algo_name=args.algo,
        graph_path=args.graph,
        grammar_path=args.grammar,
        add_contexts=args.add_contexts,
        trace_graphblas=args.trace_graphblas,
        expected_path=args.expected_path,
        time_limit_sec=args.time_limit,
        out_path=args.out,
        max_num_of_contexts=args.max_num_of_contexts,
        depth = args.depth,
        settings=settings_manager.read_args(args)
    )
    settings_manager.report_unused()


if __name__ == "__main__":       # pragma: no cover
    main(raw_args=sys.argv[1:])  # pragma: no cover
