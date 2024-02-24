import argparse
import os
import sys
from time import time
from typing import Optional, List

from src.algo_setting.preprocessor_setting import preprocess_graph_and_grammar
from src.utils.time_limit import time_limit, TimeoutException
from src.algo_setting.algo_setting import AlgoSetting
from src.algo_setting.algo_settings_manager import AlgoSettingsManager
from src.grammar.cnf_grammar_template import CnfGrammarTemplate
from src.graph.label_decomposed_graph import LabelDecomposedGraph
from src.problems.Base.template_cfg.template_cfg_all_pairs_reachability_impls import \
    ALL_PAIRS_CFL_REACHABILITY_ALGO_NAMES, \
    get_all_pairs_cfl_reachability_algo


def run_all_pairs_cflr(
        algo_name: str,
        graph_path: str,
        grammar_path: str,
        time_limit_sec: Optional[int],
        out_file: Optional[str],
        settings: List[AlgoSetting]
):
    algo = get_all_pairs_cfl_reachability_algo(algo_name)
    graph = LabelDecomposedGraph.read_from_pocr_graph_file(graph_path)
    grammar = CnfGrammarTemplate.read_from_pocr_cnf_file(grammar_path)
    graph, grammar = preprocess_graph_and_grammar(graph, grammar, settings)
    try:
        with (time_limit(time_limit_sec)):
            start = time()
            res = algo.solve(graph=graph, grammar=grammar, settings=settings)
            finish = time()
            print(f"AnalysisTime\t{finish - start}")
            print(f"#SEdges\t{res.nvals}")
            if out_file is not None:
                out_dir = os.path.dirname(out_file)
                if out_dir != "" and not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                with open(out_file, 'w') as out_file:
                    for (source, target) in res:
                        out_file.write(f"{source}\t{target}\n")
    except TimeoutException:
        print(f"AnalysisTime\tNaN")
        print(f"#SEdges\tNaN")


def main(raw_args: List[str]):
    parser = argparse.ArgumentParser(
        description="Solves the Context-Free Language Reachability (CFL-R) problem for all vertex pairs.",
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
                             'simple rules (`<NON_TERMINAL> <TERMINAL>`), and epsilon rules (`<NON_TERMINAL>`), '
                             'with values separated by whitespace characters. '
                             'Indexed symbol names should end with `_i`. '
                             'The final two lines define the starting non-terminal as: '
                             '`Count:\\n <START_NON_TERMINAL>`.')
    parser.add_argument('--time-limit', dest='time_limit', default=None, help='Sets a time limit in seconds.')
    parser.add_argument('--out', dest='out', default=None,
                        help='Specifies the output file for saving vertex pairs. '
                             'The line format is: `[START_VERTEX]\t[END_VERTEX]`. '
                             'Each line indicates a path exists from [START_VERTEX] to [END_VERTEX], '
                             'labels along which spell a word from the specified Context-Free Language (CFL).'
                        )
    settings_manager = AlgoSettingsManager()
    settings_manager.add_args(parser)
    args = parser.parse_args(raw_args)
    run_all_pairs_cflr(
        algo_name=args.algo,
        graph_path=args.graph,
        grammar_path=args.grammar,
        time_limit_sec=args.time_limit,
        out_file=args.out,
        settings=settings_manager.read_args(args)
    )
    settings_manager.report_unused()


if __name__ == "__main__":       # pragma: no cover
    main(raw_args=sys.argv[1:])  # pragma: no cover
