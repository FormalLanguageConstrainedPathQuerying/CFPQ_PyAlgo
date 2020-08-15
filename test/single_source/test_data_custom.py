import pytest
from pygraphblas import Vector

from src.algo.single_source.single_source import SingleSourceSolver
from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.useful_paths import LOCAL_CFPQ_DATA


def vecbool_to_list(xs: Vector):
    return [x[0] for x in xs]


@pytest.mark.CI
def test_case_1_graph_1(algo):
    # (0)-[a]->(1)-[a]->(2)-[b]->(3)-[b]->(4)
    # S -> a S b | a b

    test_case_1_path = LOCAL_CFPQ_DATA.joinpath('test_case_1')

    graph = LabelGraph.from_txt(test_case_1_path.joinpath('Matrices/graph_1.txt'))
    grammar = CnfGrammar.from_cnf(test_case_1_path.joinpath('Grammars/grammar.cnf'))
    single_source: SingleSourceSolver = algo(graph, grammar)

    m, _ = single_source.solve([1])
    assert vecbool_to_list(m[1]) == [3]

    m, _ = single_source.solve([0])
    assert vecbool_to_list(m[0]) == [4]


@pytest.mark.CI
def test_case_1_graph_2(algo):
    #       (6)
    #      /   \
    #    (2)   (5)
    #   /  \   /  \
    # (0) (1) (3) (4)
    # Upstream edges labeled by "a", downstream by "b"
    # S -> a S b | a b

    test_case_1_path = LOCAL_CFPQ_DATA.joinpath('test_case_1')

    graph = LabelGraph.from_txt(test_case_1_path.joinpath('Matrices/graph_2.txt'))
    grammar = CnfGrammar.from_cnf(test_case_1_path.joinpath('Grammars/grammar.cnf'))
    single_source: SingleSourceSolver = algo(graph, grammar)

    m, _ = single_source.solve([0])
    assert vecbool_to_list(m[0]) == [0, 1, 3, 4]

    m, _ = single_source.solve([2])
    assert vecbool_to_list(m[2]) == [2, 5]
