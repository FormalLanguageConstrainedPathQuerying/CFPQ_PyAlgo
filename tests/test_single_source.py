import pytest

from src.utils.file_helpers import get_file_name
from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.utils.time_profiler import SimpleTimer
from src.algo.matrix_base import matrix_base_algo
from src.algo.single_source.single_source import SingleSourceAlgoBrute, SingleSourceAlgoSmart

from suites import graph_grammar_decorator


@pytest.fixture(params=[SingleSourceAlgoBrute, SingleSourceAlgoSmart])
def algo(request):
    return request.param


@graph_grammar_decorator
def test_correctness_per_vertex(graph, grammar, algo):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    m = matrix_base_algo(g, gr)

    for i in range(g.matrices_size):
        m1 = a.solve([i])

        assert m1[i] in m[gr.start_nonterm][i]


@graph_grammar_decorator
def test_correctness(graph, grammar, algo):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    m = matrix_base_algo(g, gr)
    m1 = a.solve(range(g.matrices_size))

    assert m[gr.start_nonterm].iseq(m1)


@graph_grammar_decorator
def test_algo(graph, grammar, algo, chunk_size=None, rounds=10, warmup_rounds=2):
    g = LabelGraph.from_txt(graph)
    gr = CnfGrammar.from_cnf(grammar)
    a = algo(g, gr)

    chunks = g.chunkify(g.matrices_size if chunk_size is None else chunk_size)

    min_time, min_chunk = None, None
    max_time, max_chunk = None, None
    mean_time = None

    timer = SimpleTimer()

    # Used for prettier print
    print()

    for chunk in chunks:
        for i in range(warmup_rounds):
            a.solve(chunk)

        sum_time = 0

        for i in range(rounds):
            timer.tic()
            a.solve(chunk)
            sum_time += timer.toc()

        cur_mean = sum_time / rounds

        print(f'{get_file_name(graph)}-{get_file_name(grammar)}-{type(a).__name__}-{chunk} TIME: {round(cur_mean, 6)}s')

        if min_time is None or cur_mean < min_time:
            min_time = cur_mean
            min_chunk = chunk

        if max_time is None or cur_mean > max_time:
            max_time = cur_mean
            max_chunk = chunk

        if mean_time is None:
            mean_time = cur_mean
        else:
            mean_time += cur_mean

    mean_time /= len(chunks)

    print(f'{get_file_name(graph)}-{get_file_name(grammar)}-{type(a).__name__} MEAN TIME: {round(mean_time, 6)}s')
    print(f'{get_file_name(graph)}-{get_file_name(grammar)}-{type(a).__name__} MIN TIME: {round(min_time, 6)}s')
    print(f'{get_file_name(graph)}-{get_file_name(grammar)}-{type(a).__name__} MIN CHUNK: {min_chunk}')
    print(f'{get_file_name(graph)}-{get_file_name(grammar)}-{type(a).__name__} MAX TIME: {round(max_time, 6)}s')
    print(f'{get_file_name(graph)}-{get_file_name(grammar)}-{type(a).__name__} MAX CHUNK: {max_chunk}')