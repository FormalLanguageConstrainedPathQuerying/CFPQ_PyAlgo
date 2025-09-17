import graphblas

from graphblas.core.matrix import Matrix
from graphblas.core.dtypes import UINT64

import cfpq_add_context.labels as labels
from cfpq_add_context.utils import print_matrix_to_dot



def load_graph(file_path):
    nvertices = 0
    number_of_contexts = 0
    def get_edge_lbl(terminal):
        data_arr = terminal.split()
        _context = 0
        nonlocal number_of_contexts
        if len(data_arr) == 2:
            if "load" in data_arr[0]:
                return labels.mk_load(int(data_arr[1]))
            else:
                return labels.mk_store(int(data_arr[1]))
        elif data_arr[0] == "assign":
            return labels.mk_other(labels.ASSIGN)
        elif data_arr[0] == "alloc":
            return labels.mk_other(labels.ALLOC)
        elif "open" in data_arr[0]:
            _context =  int(data_arr[0].split('_')[1])
            res = labels.mk_open_context_from_pass(_context)

            number_of_contexts = max(number_of_contexts, _context)
            return res
        elif "close" in data_arr[0]:
            _context = int(data_arr[0].split('_')[1])
            res = labels.mk_close_context_from_ret(_context)
            number_of_contexts = max(number_of_contexts, _context)
            return res
        else: print("ERROR:", terminal)

    def get_raw_edge(line):
        nonlocal nvertices
        data = line.strip().split()
        _lbl = " ".join(data[2:])
        _from = int(data[0])
        _to = int(data[1])
        
        _max = max(_from,_to)
        nvertices = max(nvertices, _max)

        return (_from, _to, _lbl)


    with open (file_path,'r') as file:
        raw_edges = [get_raw_edge(line) for line in file if len(line.strip()) > 0 and not("_r") in line]
        #nvertices = 0
        #for (_from, _to, line) in raw_edges:
        #    _max = max(_from,_to)
        #    nvertices = max(nvertices, _max)
        
        nvertices = nvertices + 1
        
        edges = {}
        assign_lbl = get_edge_lbl("assign")
        for (v_from, v_to, terminal) in raw_edges:
            if (v_from,v_to) in edges:
                v_new = nvertices
                nvertices = nvertices + 1
                if terminal.startswith("store"):
                    edges[(v_from, v_new)] = get_edge_lbl(terminal)
                    edges[(v_new, v_to)] = assign_lbl
                else:
                    edges[(v_from, v_new)] = assign_lbl
                    edges[(v_new, v_to)] = get_edge_lbl(terminal)
            else: 
                edges[(v_from, v_to)] = get_edge_lbl(terminal)
        
        edges = [(i[0],i[1],edges[i]) for i in edges]
        #TODO Remove dup_op! It is a hack to avoid edges duplication.
        #result = Matrix.from_edgelist(edges, dtype=UINT64, nrows=nvertices + 1, ncols=nvertices + 1, name="graph",dup_op="max")
        
        result = Matrix.from_edgelist(edges, dtype=UINT64, nrows=nvertices, ncols=nvertices, name="graph")
        #print_matrix_to_dot(result, "graph.dot")
        return (result, (number_of_contexts + 1))
            
