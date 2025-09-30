import graphblas

from graphblas.core.matrix import Matrix
from graphblas.core.dtypes import UINT64

from cfpq_add_context.labels import SIGMA, SIGMA_WITHOUT_CONTEXTS, SIGMA_WITHOUT_OPEN_CONTEXTS, ALL_OPEN_CONTEXTS, mk_open_context_from_pass, mk_open_context_from_ret_r, mk_close_context_from_ret, mk_close_context_from_pass_r
from cfpq_add_context.utils import print_matrix_to_dot

def generate (number_of_contexts, depth):
    
    def mk_open_context(i):
        return mk_open_context_from_pass(i % number_of_contexts)

    def mk_close_context(i):
        return mk_close_context_from_ret(i % number_of_contexts)

    start = 0
    current_level = [start]
    edges = [(start,start,SIGMA_WITHOUT_OPEN_CONTEXTS)]
    
    for level in range(0, depth):
      next_level = range(current_level[-1] + 1, current_level[-1] + 1 + pow(number_of_contexts, level + 1) )
      print ("next = ", next_level)
      pos = 0
      for _from in current_level:
        batch_start = current_level[-1] + 1 + pos * number_of_contexts
        print("batch start = ", batch_start)
        pos += 1
        edges = (edges + 
                 [
                        edg 
                        for _to in range(batch_start, batch_start + number_of_contexts )
                        for edg in ((_from,_to, mk_open_context(_to)),(_to,_from,mk_close_context(_to)))
                 ])
      current_level = next_level
    print("curr = ", current_level)
    print("next = ", next_level)
    last_on_last_level = current_level[-1]
    final = last_on_last_level + 1
    edges = (edges + 
             [(i,i,SIGMA_WITHOUT_CONTEXTS) for i in range(1,final)] +
             [(i,final,ALL_OPEN_CONTEXTS) for i in current_level]+
             [(final,final,SIGMA)])
    print("edges: ", edges)
    result = Matrix.from_edgelist(edges, dtype=UINT64, nrows=final + 1, ncols=final + 1, name="automata")
    
    print_matrix_to_dot(result, "atm.dot")

    return result