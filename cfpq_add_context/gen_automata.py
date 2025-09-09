import graphblas

from graphblas.core.matrix import Matrix
from graphblas.core.dtypes import UINT64

from labels import SIGMA, SIGMA_WITHOUT_CONTEXTS, SIGMA_WITHOUT_OPEN_CONTEXTS, ALL_OPEN_CONTEXTS, mk_close_context, mk_open_context
from utils import print_matrix_to_dot

def generate (number_of_contexts):
    number_of_contexts = number_of_contexts * 2 # with reversed edges
    start = 0
    nvertices = number_of_contexts + number_of_contexts * number_of_contexts + 1
    final = nvertices
    first_level = [i for i in range(1, number_of_contexts + 1)]
    second_level = [i for i in range(number_of_contexts + 1, nvertices)]
    edges = [(start,start,SIGMA_WITHOUT_OPEN_CONTEXTS),(final,final,SIGMA)] + \
            [edg for on_first_level in first_level for edg in ((start, on_first_level, mk_open_context(on_first_level)),(on_first_level, start, mk_close_context(on_first_level)))] + \
            [edg for on_first_level in first_level for on_second_level in range(on_first_level * number_of_contexts + 1, on_first_level * number_of_contexts + number_of_contexts + 1) for edg in ((on_first_level, on_second_level, mk_open_context(1 + on_second_level % number_of_contexts)),(on_second_level, on_first_level, mk_close_context(1 + on_second_level % number_of_contexts)))] + \
            [(i,i,SIGMA_WITHOUT_CONTEXTS) for i in first_level + second_level] + \
            [(i,final,ALL_OPEN_CONTEXTS) for i in second_level]
    
    result = Matrix.from_edgelist(edges, dtype=UINT64, nrows=nvertices + 1, ncols=nvertices + 1, name="automata")
    
    print_matrix_to_dot(result, "atm.dot")

    return result