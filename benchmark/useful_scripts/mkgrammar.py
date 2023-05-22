import argparse
import json
import re
import typing

import cfpq_data
from pyformlang.cfg import Variable, CFG, Terminal, Production, Epsilon


def count_terminals_numbers(graph_csv) -> typing.Set[int]:
    terminals_numbers = set()

    for line in graph_csv:
        _, term, _ = line.split(' ')
        num_in_term = re.findall(r'\d+', term)
        count_num_in_term = len(num_in_term)
        if count_num_in_term == 1:
            terminals_numbers.add(int(num_in_term[0]))

    return terminals_numbers


def make_cfg(terminal_numbers: set[int]) -> CFG:
    productions: list[Production] = [
        Production(head=Variable('PT'), body=[Variable('PTh'), Terminal('alloc')]),
        Production(head=Variable('PTh'), body=[Epsilon()]),
        Production(head=Variable('PTh'), body=[Terminal('assign'), Variable('PTh')]),

        # load_{} Al store_{} PTh
        *[
            Production(
                head=Variable('PTh'),
                body=[Terminal(f'load_{t}'), Variable('Al'), Terminal(f'store_{t}'), Variable('PTh')])
            for t in terminal_numbers
        ],
        Production(head=Variable('FT'), body=[Terminal('alloc_r'), Variable('FTh')]),
        Production(head=Variable('FTh'), body=[Epsilon()]),
        Production(head=Variable('FTh'), body=[Terminal('assign_r'), Variable('FTh')]),

        # store_{}_r Al load_{}_r FTh
        *[
            Production(
                head=Variable('FTh'),
                body=[Terminal(f'store_{t}_r'), Variable('Al'), Terminal(f'load_{t}_r'), Variable('FTh')])
            for t in terminal_numbers
        ],
        Production(head=Variable('Al'), body=[Variable('PT'), Variable('FT')])
    ]
    return CFG(
        variables={Variable(nt) for nt in {'PT', 'PTh', 'FT', 'FTh', 'Al'}},  # Nonterminals
        terminals={Terminal(f'load_{t}') for t in terminal_numbers} |
                  {Terminal(f'load_{t}_r') for t in terminal_numbers} |
                  {Terminal(f'store_{t}') for t in terminal_numbers} |
                  {Terminal(f'store_{t}_r') for t in terminal_numbers} |
                  {Terminal(t) for t in {'alloc', 'alloc_r', 'assign', 'assign_r'}},
        productions=productions,
        start_symbol=Variable('PT')
    )


def make_cnf(terminal_numbers: set[int]) -> CFG:
    cfg = make_cfg(terminal_numbers)
    return cfpq_data.cfg_from_cnf(cfpq_data.cnf_from_cfg(cfg))


def convert_to_json(grammar: CFG) -> str:
    grammar_json = {
        "kind": "Grammar",
        "startSymbol": {
            "kind": "Start",
            "name": grammar.start_symbol.value,
            "nonterminal": {
                "kind": "Nonterminal",
                "name": grammar.start_symbol.value,
            }
        },
        "rules": [
            {
                "kind": "Rule",
                "head": {
                    "kind": "Nonterminal",
                    "name": rule.head.value,
                },
                "body": [
                    {
                        "kind": "Terminal",
                        "name": literal.value,
                        "regex": {
                            "kind": "Seq",
                            "symbols": [
                                {
                                    "kind": "Char",
                                    "val": ord(char)
                                } for char in literal.value
                            ]
                        }
                    } if isinstance(literal, Terminal) else
                    {
                        "kind": "Nonterminal",
                        "name": literal.value,
                    } for literal in rule.body
                ]
            } for rule in grammar.productions
        ]
    }

    return json.dumps(grammar_json)


def convert_to_text(grammar: CFG) -> str:
    return cfpq_data.cfg_to_text(grammar)


def main(args: argparse.Namespace) -> None:
    terminal_numbers = count_terminals_numbers(args.graph_csv)
    if args.grammar_type == 'cnf':
        grammar = make_cnf(terminal_numbers)
    else:
        grammar = make_cfg(terminal_numbers)

    if args.output_format == 'json':
        grammar_text = convert_to_json(grammar)
    else:
        grammar_text = convert_to_text(grammar)
    args.out_file.write(grammar_text)


if __name__ == '__main__':
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('graph_csv', type=argparse.FileType('r'))
    parser.add_argument('out_file', type=argparse.FileType('w'))
    parser.add_argument('grammar_type', choices=['cfg', 'cnf'], default='cfg')
    parser.add_argument('output_format', choices=['json', 'text'], default='text')

    main(parser.parse_args())
