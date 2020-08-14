from pygraphblas import Matrix, BOOL
from tqdm import tqdm

from src.algo.matrix_base import matrix_base_algo
from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from tests.suites import all_cfpq_data_test_cases


def print_vec(xs):
    for x in xs:
        print(x, end=' ')


@all_cfpq_data_test_cases
def test_correctness_per_vertex(graph, grammar, algo):
    CHUNK_COUNT = 20

    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    m = matrix_base_algo(g, gr)

    for chunk in tqdm(g.chunkify(max(g.matrices_size // CHUNK_COUNT, 1)), desc=graph):
        m1, _ = a.solve(chunk)
        assert m1.extract_matrix(chunk).iseq(m.extract_matrix(chunk))


@all_cfpq_data_test_cases
def test_correctness(graph, grammar, algo):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    m = matrix_base_algo(g, gr)
    m1, _ = a.solve(range(g.matrices_size))

    assert m.iseq(m1)
