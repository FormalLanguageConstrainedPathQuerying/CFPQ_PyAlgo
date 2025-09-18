import graphblas

from graphblas.core.matrix import Matrix

def print_matrix_to_dot(matrix, file):
    edges = matrix.to_edgelist()
    edges = zip(edges[0], edges[1])
    with open(file, 'w') as f:
        print("digraph g{", file = f)
        for (_edg, _lbl) in edges:
            print (str (_edg[0]) + " -> " + str(_edg[1]) + "[label=" + str(_lbl) +"]", file = f)
        print("}", file = f)

def verify(result, expected_path):
    with open(expected_path, 'r') as file:
        expected = set([(int(line[0]),int(line[2])) for line in  [line.strip().split(" ") for line in file]])
        res = expected.issubset(result)
        if not res:
            for i in expected.difference(result):
                print("Missed: ", i)
        return res