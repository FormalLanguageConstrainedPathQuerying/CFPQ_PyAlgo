from cfpq_data import DATASET, graph_from_dataset, cfg_to_txt, nodes_to_integers, get_labels, change_edges

from cfpq_data.grammars.samples.rdf import g1, g2, geo
from cfpq_data.grammars.samples.cycle import a_star_0, a_star_1, a_star_2
from cfpq_data.grammars.samples.barabasi_albert import an_bm_cm_dn
from cfpq_data.grammars.samples.binomial import sg
from cfpq_data.grammars.samples.memory_aliases import g1 as g1_ma, g2 as g2_ma
from cfpq_data.grammars.samples.two_cycles import brackets

from pathlib import Path

import argparse
import os

DEFAULT_PATH = Path("../data/")
DEFAULT_GRAPH_PATH = DEFAULT_PATH.joinpath("Graphs/")
DEFAULT_GRAMMAR_PATH = DEFAULT_PATH.joinpath("Grammars/")

GRAMMARS_BY_TYPE = {
    "rdf": [g1, g2, geo],
    "cycle": [a_star_0, a_star_1, a_star_2],
    "barabasi_albert": [an_bm_cm_dn],
    "bimomial": [sg],
    "memory_aliases": [g1_ma, g2_ma],
    "two_cycles": [brackets]
}

GRAMMARS_BY_NAME = {
    g1: "g1",
    g2: "g2",
    geo: "geo",
    a_star_0: "a_star_0",
    a_star_1: "a_star_1",
    a_star_2: "a_star_2",
    an_bm_cm_dn: "an_bm_cm_dn",
    sg: "sg",
    g1_ma: "g1_ma",
    g2_ma: "g2_ma",
    brackets: "brackets"
}

CONFIG = {
    "subClassOf": "sco",
    "type": "t",
    "broaderTransitive": "bt",
    "http://yacc/D": "d",
    "http://yacc/A": "a"
}


def graph_to_txt(graph, path, config):
    with open(path, "w") as fout:
        for u, v, edge_labels in graph.edges(data=True):
            for label in edge_labels.values():
                if config[str(label)] == "other":
                    continue
                fout.write(f"{u} {config[str(label)]} {v}\n")
                fout.write(f"{v} {config[str(label)]}_r {u}\n")


def load_graph_by_type(type):
    for name_graph in DATASET[type].keys():
        load_graph_by_name(name_graph)


def load_graph_by_name(name_graph):
    g = nodes_to_integers(graph_from_dataset(name_graph, verbose=False), verbose=False)
    config_cur = dict()
    for label in get_labels(g, verbose=False):
        label_str = str(label).split("#")
        if len(label_str) < 2:
            config_cur.update({str(label): "other"})
        else:
            l = CONFIG.get(label_str[1], "other")
            config_cur.update({str(label): l})
    graph_to_txt(g, DEFAULT_GRAPH_PATH.joinpath(name_graph), config_cur)


def load_grammar_by_type(name_grammar):
    for grammar in GRAMMARS_BY_TYPE[name_grammar]:
        cfg_to_txt(grammar, DEFAULT_GRAMMAR_PATH.joinpath(GRAMMARS_BY_NAME[grammar]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tools for download graphs and grammars")

    types_graphs = DATASET.keys()
    parser.add_argument('-graph_type', dest="graph_type", default=None, choices=types_graphs)
    parser.add_argument('-graph_name', dest="graph_name", default=None)
    types_grammars = GRAMMARS_BY_TYPE.keys()
    parser.add_argument('-grammar_type', dest="grammar_type", default=None, choices=types_grammars)

    if os.path.exists(DEFAULT_PATH):
        if not os.path.exists(DEFAULT_GRAPH_PATH):
            os.mkdir(DEFAULT_GRAPH_PATH)
        if not os.path.exists(DEFAULT_GRAMMAR_PATH):
            os.mkdir(DEFAULT_GRAMMAR_PATH)
    else:
        os.mkdir(DEFAULT_PATH)
        os.mkdir(DEFAULT_GRAPH_PATH)
        os.mkdir(DEFAULT_GRAMMAR_PATH)

    args = parser.parse_args()
    if args.graph_type is not None:
        load_graph_by_type(args.graph_type)

    if args.graph_name is not None:
        load_graph_by_name(args.graph_name)

    if args.grammar_type is not None:
        load_grammar_by_type(args.grammar_type)
