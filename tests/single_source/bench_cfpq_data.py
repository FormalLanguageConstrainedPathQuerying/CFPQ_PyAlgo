import pytest

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from tests.suites import all_cfpq_data_test_cases


@pytest.mark.parametrize('chunk_size', [None, *[2 ** i for i in range(14)]])
@all_cfpq_data_test_cases
def test_single_source_benchmark_total(graph, grammar, algo, chunk_size, benchmark):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)
    chunks = g.chunkify(g.matrices_size if chunk_size is None else chunk_size)

    def run_suite():
        for chunk in chunks:
            a.solve(chunk)

    benchmark.pedantic(run_suite, rounds=5, iterations=1, warmup_rounds=0)
