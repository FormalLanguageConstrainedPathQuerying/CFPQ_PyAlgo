import graphblas

from cfpq_add_context.load_graph import load_graph
from cfpq_add_context.intersection import intersection
from cfpq_add_context.gen_automata import generate
from graphblas.core.dtypes import BOOL, UINT64
from graphblas.core.matrix import Matrix, Vector
from graphblas import op
from graphblas.core.operator import Monoid, BinaryOp, SelectOp, UnaryOp

from cfpq_matrix.block.block_matrix_space_impl import BlockMatrixSpaceImpl
from cfpq_model.cnf_grammar_template import Symbol
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph
from cfpq_add_context.utils import print_matrix_to_dot

import time

def indexed_to_boolean_decomposition(graph, block_count):
    vertex_count = graph.nrows
    edges = graph.to_edgelist()
    edges = zip(edges[0], edges[1])
    new_edges = [(_edg[0] + vertex_count * _lbl, _edg[1]) for (_edg, _lbl) in edges]
    result = Matrix.from_edgelist(new_edges, values=True, dtype=BOOL, nrows = block_count * vertex_count,
                                             ncols=vertex_count, name = "boolean_decomposition_of_indexed")
    return result

def transitive_reduction(assigns, vertices_with_other_edges):
    result = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "reduced_assigns")
    endpoints = vertices_with_other_edges.diag(name = "endpoints") 
    assigns_transposed = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "assigns_transposed")
    assigns_transposed("any") << assigns.T
    frontier = vertices_with_other_edges.diag(name = "frontier")
    #filter("any") << frontier
    visited = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "visited")
    visited("any") << frontier
    while True:
        print ("Frontier nvals = ", frontier.nvals)
        #print("Frontier: ", frontier)
        if frontier.nvals == 0:
            break
        new_frontier = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "new_frontier")        
        new_frontier(~visited.S) << Matrix.mxm(frontier, assigns, "any_pair")
        #print("New frontier: ", new_frontier)
        filter = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "filter")
        #print("Endpoints: ", endpoints)
        x = new_frontier.reduce_rowwise("any").diag() 
        filter(~x.S) << endpoints

        #print("Filter: ", filter)        
        #to_result = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "to_result")
        #to_result << (Matrix.mxm(new_frontier, filter, "any_pair"))
        #print("To result: ", to_result)

        result("any") << (Matrix.mxm(new_frontier, filter, "any_pair"))

        print ("Result nvals = ", result.nvals)

        visited("any") << new_frontier
        
        new_frontier_2 = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "new_frontier_2")
        new_frontier_2(~result.S) << new_frontier
        #print("New frontier 2: ", new_frontier_2)
        frontier = new_frontier_2

    return result

def to_label_decomposed_graph(graph, automata_size, initial_graph_size):
    vertex_count = graph.nrows
    alloc = Matrix(BOOL, graph.ncols, graph.nrows, name = "alloc_after_intersection")
    alloc << graph.select(graphblas.select.select_alloc)
    print("Boolean matrix for alloc nvals: ", alloc.nvals)
    
    alloc_r = Matrix(BOOL, graph.ncols, graph.nrows, name = "alloc_r_after_intersection")
    alloc_r << alloc.T
    print("Boolean matrix for alloc_r nvals: ", alloc_r.nvals)

    print("mask start")
    mask_v = Vector(BOOL, graph.ncols, name = "mask_vector")
    #exit_mask_v = Vector(BOOL, graph.ncols, name = "exit_mask_vector")
    mask_v("any") << alloc.reduce_columnwise("any")
    mask_v("any") << alloc.reduce_rowwise("any")

    print("entrypoints start")

    entrypoints = Vector(bool,graph.nrows, name="entrypoints")
    entrypoints << graph.reduce_columnwise(op.lor)
    #mask_v(op.lor) << Vector.from_coo(list(set(range(0,graph.nrows)).difference(entrypoints.to_coo(values=False)[0])), values=True, dtype = BOOL)
    
    # !!! mask_v("any") << Vector.from_coo([i * automata_size for i in range(0, initial_graph_size)], values=True, dtype = BOOL, size = graph.ncols)

    load_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "load_i_after_intersection")
    load_i << graph.select(graphblas.select.select_load).apply(graphblas.unary.decode_load)
    print("Matrix for load_i nvals: ", load_i.nvals)

    store_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "store_i_after_intersection")
    store_i << graph.select(graphblas.select.select_store).apply(graphblas.unary.decode_store)
    print("Matrix for store_i nvals: ", store_i.nvals)

    mask_v("any") << load_i.reduce_columnwise("any")
    mask_v("any") << load_i.reduce_rowwise("any")

    mask_v("any") << store_i.reduce_columnwise("any")
    mask_v("any") << store_i.reduce_rowwise("any")

    store_block_count = store_i.reduce_scalar("max").get(0) + 1
    load_block_count = load_i.reduce_scalar("max").get(0) + 1
    block_count = max(store_block_count, load_block_count)    

    boolean_decompose_load = indexed_to_boolean_decomposition(load_i, block_count)
    print("Boolean matrix for load nvals: ", boolean_decompose_load.nvals)

    boolean_decompose_store = indexed_to_boolean_decomposition(store_i, block_count)
    print("Boolean matrix for store nvals: ", boolean_decompose_store.nvals)

    load_r_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "load_r_i_after_intersection")
    load_r_i << load_i.T
    print("Matrix for load_r_i nvals: ", load_r_i.nvals)

    boolean_decompose_load_r = indexed_to_boolean_decomposition(load_r_i, block_count)
    print("Boolean matrix for load_r nvals: ", boolean_decompose_load_r.nvals)

    store_r_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "store_r_i_after_intersection")
    store_r_i << store_i.T
    print("Matrix for store_r_i nvals: ", store_r_i.nvals)

    boolean_decompose_store_r = indexed_to_boolean_decomposition(store_r_i, block_count)
    print("Boolean matrix for store_r nvals: ", boolean_decompose_store_r.nvals)

    
    #mask_v("any") << exit_mask_v
    #assign_mask = mask_v.diag(name = "assign_mask")
    #exit_mask = exit_mask_v.diag(name = "exit_mask")
    
    assign = Matrix(BOOL, graph.ncols, graph.nrows, name = "assign_after_intersection")
    assign << graph.select(graphblas.select.select_assign)
    print("Boolean matrix for assign nvals: ", assign.nvals)
    
    
    assign << transitive_reduction(assign, mask_v)

    assign_r = Matrix(BOOL, graph.ncols, graph.nrows, name = "assign_r_after_intersection")
    assign_r << assign.T
    print("Boolean matrix for assign_r nvals: ", assign_r.nvals)

    #print_matrix_to_dot(assign_r,"assign_r.dot")

    matrices: Dict[Symbol, Matrix] = {}

    matrices[Symbol('alloc')] = alloc
    matrices[Symbol('alloc_r')] = alloc_r

    matrices[Symbol('assign')] = assign
    matrices[Symbol('assign_r')] = assign_r

    matrices[Symbol('store_i')] = boolean_decompose_store
    matrices[Symbol('load_i')] = boolean_decompose_load
    matrices[Symbol('store_r_i')] = boolean_decompose_store_r
    matrices[Symbol('load_r_i')] = boolean_decompose_load_r

    return LabelDecomposedGraph(
                vertex_count=vertex_count,
                block_matrix_space=BlockMatrixSpaceImpl(n=vertex_count, block_count=block_count),
                dtype=BOOL,
                matrices=matrices
            )

def add_context(file_path, max_num_of_contexts):
    load_graph_start = time.perf_counter()
    
    graph,number_of_contexts = load_graph(file_path, max_num_of_contexts)
    
    load_graph_end = time.perf_counter()
    print("Graph loaded in ", load_graph_end - load_graph_start)
    print("Vertices in graph: ", graph.ncols)
    print("Edges in graph: ", graph.nvals)
    print("Numer of contexts: ", number_of_contexts)
    
    automata = generate(number_of_contexts)
    
    automata_generation_end = time.perf_counter()
    print("Automata generated in ", automata_generation_end - load_graph_end)
    print("Vertices in automata: ", automata.ncols)
    print("Edges in automata: ", automata.nvals)

    result = intersection(graph, automata)

    intersection_end = time.perf_counter()
    print("Graph and automata intersection competed in ", intersection_end - automata_generation_end)
    print("Vertices in intersection: ", result.ncols)
    print("Edges in intersection: ", result.nvals)
    
    decomposed_result = to_label_decomposed_graph(result, automata.nrows, graph.nrows)
    decomposition_end = time.perf_counter()
    print("Graph decomposition completed in ", decomposition_end - intersection_end)

    return (decomposed_result, graph.ncols)

def select_result(atm_size):
    def inner(x,i,j,k):
        return i % atm_size == 0
    return inner

SelectOp.register_new("select_result", select_result, parameterized = True)

def normalize(solver_result, initial_graph_nvertices):
    
    normalization_start = time.perf_counter()
    
    atm_size = solver_result.ncols // initial_graph_nvertices
    start_vertices = set([i * atm_size for i in range(0,initial_graph_nvertices)])
    solver_result = solver_result.select(graphblas.select.select_result(atm_size))
    edges = solver_result.to_edgelist()
    edges = zip(edges[0], edges[1])
    new_edges = set([(_edg[0] // atm_size, _edg[1] // atm_size) for (_edg, _lbl) in edges if _edg[0] in start_vertices])
    #new_edges = set([(_edg[0] // atm_size, _edg[1] // atm_size) for (_edg, _lbl) in edges])
    result = Matrix.from_edgelist(new_edges, values=True, dtype=BOOL, nrows = initial_graph_nvertices,
                                             ncols=initial_graph_nvertices, name = "normalized_solver_result")
    normalization_end = time.perf_counter()
    print("Normalization of solver result done in ", normalization_end - normalization_start)
    
    return result


def transitive_reduction_test():
    m = Matrix.from_edgelist([(0,1),(1,2),(1,3)],values=True,dtype=BOOL,nrows=4,ncols=4)
    v = Vector.from_coo([0,2,3],values=True)
    return transitive_reduction(m,v)
