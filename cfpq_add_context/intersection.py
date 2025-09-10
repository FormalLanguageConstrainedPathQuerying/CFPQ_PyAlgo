import graphblas

from graphblas.core.matrix import Matrix
from graphblas.core.vector import Vector
from graphblas.core.operator import Semiring, Monoid, SelectOp
from graphblas.core.dtypes import UINT64
from graphblas import op, semiring
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

def filter_not_zero_op(x,i,j,k):
    return x > 0

SelectOp.register_new("filter_not_zero", filter_not_zero_op)

def intersection (graph, automata) :
    intersection = kronecker(graph, automata)
    #TODO remove when moved to patched kronecker
    intersection << intersection.select(graphblas.select.filter_not_zero)

    print_matrix_to_dot(intersection, "kron.dot")
    
    sources = [i * automata.nrows for i in range(0,graph.nrows)]

    reachable_vertices_mask = bfs(intersection, sources).diag(name="reachable_vertices_mask")
    
    result = Matrix(intersection.dtype, intersection.nrows, intersection.ncols, name = "filtered intersection")
    result << reachable_vertices_mask @ intersection
    print_matrix_to_dot(result, "kron_filtered.dot")
    return result


def test():
    graph_edges = [(0,0,(labels.mk_open_context(1)))]
    automata = gen_automata.generate(2)
    
    graph = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=1, ncols=1, name="graph")

    i = intersection(graph, automata)
    

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
    graph_edges = [(0,0,1),(0,1,2),(1,1,3),(0,2,4),(2,0,5),(2,2,3)]    
    
    graph1 = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=6, ncols=6, name="graph1")
    graph2 = Matrix.from_edgelist(graph_edges,dtype=UINT64, nrows=6, ncols=6, name="graph2")

    i = graph1.kronecker(graph2)
    print_matrix_to_dot(i, "kron_build.dot")