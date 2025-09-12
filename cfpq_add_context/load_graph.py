import graphblas

from graphblas.core.matrix import Matrix
from graphblas.core.dtypes import UINT64

import cfpq_add_context.labels as labels
from cfpq_add_context.utils import print_matrix_to_dot



def load_graph(file_path):
    nvertices = 0
    number_of_contexts = 0
    def get_edge_lbl(data_arr):
        _context = 0
        nonlocal number_of_contexts
        if len(data_arr) == 4:
            if "load_r" in data_arr[2]:
                return labels.mk_load_r(int(data_arr[3]))
            elif "load" in data_arr[2]:
                return labels.mk_load(int(data_arr[3]))
            elif "store_r" in data_arr[2]:
                return labels.mk_store_r(int(data_arr[3]))
            else:
                return labels.mk_store(int(data_arr[3]))
        elif data_arr[2] == "assign":
            return labels.mk_other(labels.ASSIGN)
        elif data_arr[2] == "assign_r":
            return labels.mk_other(labels.ASSIGN_R)
        elif data_arr[2] == "alloc":
            return labels.mk_other(labels.ALLOC)
        elif data_arr[2] == "alloc_r":
            return labels.mk_other(labels.ALLOC_R)
        elif "open" in data_arr[2]:
            if "_r_" in data_arr[2]:
                _context = 2 * (1 + int(data_arr[2].split('_')[2]))
            else:
                _context =  2 * (1 + int(data_arr[2].split('_')[1])) + 1
            number_of_contexts = max(number_of_contexts, _context)
            return labels.mk_open_context(_context)
        else:
            if "_r_" in data_arr[2]:
                _context = 2 * int(data_arr[2].split('_')[2])
            else:
                _context = 2 * int(data_arr[2].split('_')[1]) + 1
            number_of_contexts = max(number_of_contexts, _context)
            return labels.mk_close_context(_context)

    def handle_line(line):
        nonlocal nvertices
        data = line.strip().split()
        _lbl = get_edge_lbl(data)
        _from = int(data[0])
        _to = int(data[1])
        
        _max = max(_from,_to)
        nvertices = max(nvertices, _max)

        return (_from, _to, _lbl)

    with open (file_path,'r') as file:
        edges = [handle_line(line) for line in file if len(line.strip()) > 0]
        #TODO Remove dup_op! It is a hack to avoid edges duplication.
        result = Matrix.from_edgelist(edges, dtype=UINT64, nrows=nvertices + 1, ncols=nvertices + 1, name="graph",dup_op="max")
        #print_matrix_to_dot(result, "graph.dot")
        return (result, (number_of_contexts // 2) + 1)
            
