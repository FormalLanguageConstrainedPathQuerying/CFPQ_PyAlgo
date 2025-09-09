import graphblas

from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector
from graphblas.core.operator import Semiring, Monoid, SelectOp
from graphblas.core.dtypes import UINT64
from graphblas import op, semiring
from numba import njit, jit
import gen_automata

import labels
from utils import print_matrix_to_dot

def kronecker (graph, automata):
    result = Matrix(graph.dtype, graph.nrows * automata.nrows, graph.ncols * automata.ncols, name="intersection")
    result << graph.kronecker(automata, graphblas.monoid.labels_intersection)
    return result

def bfs (matrix, sources):
    n = matrix.nrows
    print ("n = ", n)
    
    reachable = Vector.from_coo(sources, True, size=n, name="reachable")
    frontier = Vector.from_coo(sources, True, size=n, name="frontier")
    
    print("frontier nvals = ",  frontier.nvals)
    
    while frontier.nvals > 0:
    
        new_frontier = Vector(bool, size=n)
        new_frontier(~reachable.S) << semiring.any_first(frontier @ matrix)
        
        print("new_frontier nvals = ",  new_frontier.nvals)

        if new_frontier.nvals == 0:
            break

        reachable(op.land) << new_frontier
        
        frontier = new_frontier
    
    return reachable


def filter_reachable_op(reachable_vertices):
    _reachable_vertices = set(reachable_vertices)
    def inner(x,i,j,k):        
        return i in _reachable_vertices and j in _reachable_vertices
    return inner

SelectOp.register_new("filter_reachable", filter_reachable_op, parameterized=True, is_udt=True)

def filter_not_zero_op(x,i,j,k):
    return x > 0

SelectOp.register_new("filter_not_zero", filter_not_zero_op)

def intersection (graph, automata) :
    intersection = kronecker(graph, automata)
    #TODO remove when moved to patched kronecker
    intersection << intersection.select(graphblas.select.filter_not_zero)

    print_matrix_to_dot(intersection, "kron.dot")
    
    sources = [i * automata.nrows for i in range(0,graph.nrows)]
    #reachable = frozenset(bfs(intersection, sources).to_coo(values=False)[0])
    #reachable_vertices = set(bfs(intersection, sources).to_coo(values=False)[0])

    reachable_vertices_mask = bfs(intersection, sources).diag(name="reachable_vertices_mask")
    
    #def filter_reachable_op(x,i,j,k):
    #    return i in reachable_vertices and j in reachable_vertices

    #SelectOp.register_new("filter_reachable", filter_reachable_op, is_udt=True)

    #print("reachable = ", reachable_vertices)
    #print("num of reachable = ", len(reachable_vertices))
    #edges = intersection.to_edgelist()
    #edges = zip(edges[0],edges[1])
    #new_edges = [(_edg[0],_edg[1],_lbl) for (_edg,_lbl) in  edges if _edg[0] in reachable_vertices and _edg[1] in reachable_vertices]
    #result = Matrix.from_edgelist(new_edges, dtype=intersection.dtype, nrows=intersection.nrows, ncols=intersection.ncols, name = "filtered intersection")
    result = Matrix(intersection.dtype, intersection.nrows, intersection.ncols, name = "filtered intersection")
    #result << intersection.select(graphblas.select.filter_reachable(reachable_vertices=reachable_vertices))
    #result << intersection.select(graphblas.select.filter_reachable)
    result << reachable_vertices_mask @ intersection
    print_matrix_to_dot(result, "kron_filtered.dot")
    return result


def test():
    graph_edges = [(0,0,(labels.mk_open_context(1)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=1, ncols=1, name="graph")

    i = intersection(graph, automata)
    
    #print_matrix_to_dot(intersection, "kron.dot")

def test2():
    graph_edges = [(0,0,(labels.mk_open_context(1))),(0,1,(labels.mk_open_context(1))),(1,1,(labels.mk_close_context(1)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=2, ncols=2, name="graph")

    i = intersection(graph, automata)

def test3():
    graph_edges = [(0,1,(labels.mk_open_context(1))),(1,2,(labels.mk_close_context(1)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=3, ncols=3, name="graph")

    i = intersection(graph, automata)

def test4():
    graph_edges = [(0,1,(labels.mk_open_context(1))),(1,2,(labels.mk_close_context(1))),(0,3,(labels.mk_open_context(2))),(3,2,(labels.mk_close_context(2)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=4, ncols=4, name="graph")

    i = intersection(graph, automata)

def test5():
    graph_edges = [(0,1,(labels.mk_open_context(1))),(1,2,(labels.mk_open_context(2))),(2,3,(labels.mk_close_context(2))),(3,4,(labels.mk_close_context(1)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=5, ncols=5, name="graph")

    i = intersection(graph, automata)

def test6():
    graph_edges = [(0,1,(labels.mk_open_context(1))),(1,2,(labels.mk_other(1))),(2,3,(labels.mk_close_context(1))),(4,1,(labels.mk_open_context(2))),(2,5,(labels.mk_close_context(2)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=6, ncols=6, name="graph")

    i = intersection(graph, automata)

def test7():
    graph_edges = [(0,1,(labels.mk_open_context(1))),(1,2,(labels.mk_other(1))),(2,3,(labels.mk_close_context(1))),(4,1,(labels.mk_open_context(2))),(2,5,(labels.mk_close_context(2))),(3,4,(labels.mk_other(2)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=7, ncols=7, name="graph")

    i = intersection(graph, automata)

def test8():
    automata1 = gen_automata.generate(1)
    automata2 = gen_automata.generate(1)
    i = intersection(automata1, automata2)