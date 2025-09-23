import graphblas

from cfpq_add_context.load_graph import load_graph
from cfpq_add_context.intersection import intersection
from cfpq_add_context.gen_automata import generate
from graphblas.core.dtypes import BOOL, UINT64
from graphblas.core.matrix import Matrix, Vector
from graphblas import op

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

def transitive_reduction(assigns, mask):
    result = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "reduced_assigns")
    result << Matrix.mxm(mask, assigns, "land_lor")
    total = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "closure")
    unused_assigns = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "unused_assigns")
    unused_assigns(~result.S) << assigns
    closure = unused_assigns
    total("lor") << closure
    #while closure.nvals > 0:
    while True:
        print ("Closure nvals = ", closure.nvals)
        closure << Matrix.mxm(closure, unused_assigns, "land_lor")
        result("lor") << Matrix.mxm(closure, mask, "land_lor")
        new_closure = Matrix(BOOL, assigns.ncols, assigns.ncols, name = "closure")
        new_closure(~result.S) << closure
        nnz = total.nvals
        total("lor") << closure
        if total.nvals == nnz:
            break
    return result

def to_label_decomposed_graph(graph, automata_size, initial_graph_size):
    vertex_count = graph.nrows
    alloc = Matrix(BOOL, graph.ncols, graph.nrows, name = "alloc_after_intersection")
    alloc << graph.select(graphblas.select.select_alloc)
    print("Boolean matrix for alloc nvals: ", alloc.nvals)
    
    alloc_r = Matrix(BOOL, graph.ncols, graph.nrows, name = "alloc_r_after_intersection")
    alloc_r << alloc.T
    print("Boolean matrix for alloc_r nvals: ", alloc_r.nvals)

    #print("mask start")
    #mask_v = Vector(BOOL, graph.ncols, name = "mask_vector")
    #mask_v(op.lor) << alloc.reduce_columnwise("lor")  
    #mask_v(op.lor) << alloc.reduce_rowwise("lor")

    #print("entrypoints start")

    #entrypoints = Vector(bool,graph.nrows, name="entrypoints")
    #entrypoints << graph.reduce_columnwise(op.lor)
    #mask_v(op.lor) << Vector.from_coo(list(set(range(0,graph.nrows)).difference(entrypoints.to_coo(values=False)[0])), values=True, dtype = BOOL)
    
    #mask_v(op.lor) << Vector.from_coo([i * automata_size for i in range(0, initial_graph_size)], values=True, dtype = BOOL, size= graph.ncols)

    load_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "load_i_after_intersection")
    load_i << graph.select(graphblas.select.select_load).apply(graphblas.unary.decode_load)
    print("Matrix for load_i nvals: ", load_i.nvals)

    store_i = Matrix(UINT64, graph.ncols, graph.nrows, name = "store_i_after_intersection")
    store_i << graph.select(graphblas.select.select_store).apply(graphblas.unary.decode_store)
    print("Matrix for store_i nvals: ", store_i.nvals)

    #mask_v(op.lor) << load_i.reduce_columnwise("lor")
    #mask_v(op.lor) << load_i.reduce_rowwise("lor")

    #mask_v(op.lor) << store_i.reduce_columnwise("lor")
    #mask_v(op.lor) << store_i.reduce_rowwise("lor")

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

    
    
    #assign_mask = mask_v.diag(name = "assign_mask")
    
    assign = Matrix(BOOL, graph.ncols, graph.nrows, name = "assign_after_intersection")
    assign << graph.select(graphblas.select.select_assign)
    print("Boolean matrix for assign nvals: ", assign.nvals)
    
    
    #assign << transitive_reduction(assign, assign_mask)

    #assign_res = Matrix(BOOL, graph.ncols, graph.nrows, name = "assign_after_transitive_reduction")
    #assign_1 = Matrix.mxm(assign_mask, assign, "land_lor")
    #print("Boolean matrix for assign of length 1 nvals: ", assign_1.nvals)
    #assign_to_use(~assign_1) << assign
    #_continue = True
    #while _continue:
    #    assign_i = Matrix.mxm(assign_to_use, assign_to_use, "land_lor")
    #    print("Boolean matrix for assign of length 1 nvals: ", assign_i.nvals)
    #    assign_i_use = Matrix.mxm(assign_mask, assign_i, "land_lor")
    #    assign_res("lor") << assign_i_use

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
    print("Graph decomposition competed in ", decomposition_end - intersection_end)

    return (decomposed_result, graph.ncols)

def normalize(solver_result, initial_graph_nvertices):
    
    normalization_start = time.perf_counter()
    
    c = solver_result.ncols // initial_graph_nvertices
    start_vertices = set([i * c for i in range(0,initial_graph_nvertices)])
    edges = solver_result.to_edgelist()
    edges = zip(edges[0], edges[1])
    new_edges = set([(_edg[0] // c, _edg[1] // c) for (_edg, _lbl) in edges if _edg[0] in start_vertices])
    result = Matrix.from_edgelist(new_edges, values=True, dtype=BOOL, nrows = initial_graph_nvertices,
                                             ncols=initial_graph_nvertices, name = "normalized_solver_result")
    normalization_end = time.perf_counter()
    print("Normalization of solver result done in ", normalization_end - normalization_start)
    
    return result


