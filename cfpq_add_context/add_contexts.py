import graphblas

from cfpq_add_context.load_graph import load_graph
from cfpq_add_context.intersection import intersection
from cfpq_add_context.gen_automata import generate
from graphblas.core.dtypes import BOOL, UINT64
from graphblas.core.matrix import Matrix

from cfpq_matrix.block.block_matrix_space_impl import BlockMatrixSpaceImpl
from cfpq_model.cnf_grammar_template import Symbol
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph
from cfpq_add_context.utils import print_matrix_to_dot

import time

def indexed_to_boolean_decomposition(graph, block_count):
    #print("graph = ", graph)
    #print("block count = ", block_count )
    vertex_count = graph.nrows
    edges = graph.to_edgelist()
    edges = zip(edges[0], edges[1])
    new_edges = [(_edg[0] + vertex_count * _lbl, _edg[1]) for (_edg, _lbl) in edges]
    result = Matrix.from_edgelist(new_edges, values=True, dtype=BOOL, nrows = block_count * vertex_count,
                                             ncols=vertex_count, name = "boolean_decomposition_of_indexed")
    return result

def to_label_decomposed_graph(graph):
    vertex_count = graph.nrows
    alloc = Matrix(BOOL, graph.ncols, graph.nrows, name = "alloc_after_intersection")
    alloc << graph.select(graphblas.select.select_alloc)
    print("Boolean matrix for alloc nvals: ", alloc.nvals)
    
    alloc_r = Matrix(BOOL, graph.ncols, graph.nrows, name = "alloc_r_after_intersection")
    #alloc_r << graph.select(graphblas.select.select_alloc_r)
    alloc_r << alloc.T
    print("Boolean matrix for alloc_r nvals: ", alloc_r.nvals)

    assign = Matrix(BOOL, graph.ncols, graph.nrows, name = "assign_after_intersection")
    assign << graph.select(graphblas.select.select_assign)
    print("Boolean matrix for assign nvals: ", assign.nvals)
    
    assign_r = Matrix(BOOL, graph.ncols, graph.nrows, name = "assign_r_after_intersection")
    #assign_r << graph.select(graphblas.select.select_assign_r)
    #assign_r << assign_r + graph.select(graphblas.select.select_pass_and_return).T
    assign_r << assign.T
    print("Boolean matrix for assign_r nvals: ", assign_r.nvals)

    #print_matrix_to_dot(assign_r,"assign_r.dot")

    load_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "load_i_after_intersection")
    load_i << graph.select(graphblas.select.select_load).apply(graphblas.unary.decode_load)

    load_r_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "load_r_i_after_intersection")
    #load_r_i << graph.select(graphblas.select.select_load_r).apply(graphblas.unary.decode_load_r)
    load_r_i << load_i.T

    store_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "store_i_after_intersection")
    store_i << graph.select(graphblas.select.select_store).apply(graphblas.unary.decode_store)

    store_r_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "store_r_i_after_intersection")
    #store_r_i << graph.select(graphblas.select.select_store_r).apply(graphblas.unary.decode_store_r)
    store_r_i << store_i.T

    store_block_count = store_i.reduce_scalar("max").get(0) + 1
    load_block_count = load_i.reduce_scalar("max").get(0) + 1
    block_count = max(store_block_count, load_block_count)

    boolean_decompose_load = indexed_to_boolean_decomposition(load_i, block_count)
    print("Boolean matrix for load nvals: ", boolean_decompose_load.nvals)

    boolean_decompose_load_r = indexed_to_boolean_decomposition(load_r_i, block_count)
    print("Boolean matrix for load_r nvals: ", boolean_decompose_load_r.nvals)

    boolean_decompose_store = indexed_to_boolean_decomposition(store_i, block_count)
    print("Boolean matrix for store nvals: ", boolean_decompose_store.nvals)

    boolean_decompose_store_r = indexed_to_boolean_decomposition(store_r_i, block_count)
    print("Boolean matrix for store_r nvals: ", boolean_decompose_store_r.nvals)
    

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

def add_context(file_path):
    load_graph_start = time.perf_counter()
    
    graph,number_of_contexts = load_graph(file_path)
    
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
    
    decomposed_result = to_label_decomposed_graph(result)
    decomposition_end = time.perf_counter()
    print("Graph decomposition competed in ", decomposition_end - intersection_end)

    return decomposed_result


