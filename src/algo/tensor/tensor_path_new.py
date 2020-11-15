from pygraphblas import *

from src.graph.label_graph import LabelGraph
from src.grammar.rsa import RecursiveAutomaton


class Paths:
    def __init__(self, level, current_vertex, use=True):
        self.level = level
        self.current_vertex = current_vertex
        self.use = use

    def close(self):
        self.use = False


class TensorPaths:
    def __init__(self, graph: LabelGraph, rsa: RecursiveAutomaton, tc: Matrix, max_len):
        self.graph = graph
        self.rsa = rsa
        self.tc = tc
        self.max_len = max_len
        self.graph_size = graph.matrices_size

    def gen_paths(self, start, finish, current_len):

        q = Vector.sparse(BOOL, self.tc.nrows)
        q[start] = True
        supposed_paths = [Paths(Vector.sparse(UINT32, self.tc.nrows), q)]
        paths = []

        for level in range(current_len):
            size = len(supposed_paths)
            for i in range(size):

                if not supposed_paths[i].use:
                    continue

                supposed_paths[i].level.assign_scalar(level, mask=supposed_paths[i].current_vertex)

                if finish in supposed_paths[i].level:
                    paths.append(supposed_paths[i])

                supposed_paths[i].current_vertex = supposed_paths[i].current_vertex.vxm(self.tc,
                                                                                        mask=supposed_paths[
                                                                                            i].current_vertex,
                                                                                        desc=descriptor.ooco)
                if supposed_paths[i].current_vertex.nvals == 0:
                    supposed_paths[i].close()

                if supposed_paths[i].current_vertex.nvals != 1:
                    first_iter = True
                    for j in supposed_paths[i].current_vertex:
                        new_current = Vector.sparse(BOOL, self.tc.nrows)
                        new_current[j[0]] = True
                        if first_iter:
                            supposed_paths[i].current_vertex = new_current
                            first_iter = False
                        else:
                            new_level = supposed_paths[i].level.dup()
                            supposed_paths.append(Paths(new_level, new_current))

        return paths

    def solve(self, start, finish, N):
        return self.get_paths(start, finish, N, self.max_len)

    def get_paths(self, start, finish, N, current_len):

        supposed_paths = self.gen_paths(self.rsa.start_state()[N] * self.graph_size + start,
                                        self.rsa.finish_states()[N][0] * self.graph_size + finish, current_len)

        result_paths = []
        for path in supposed_paths:
            path_list = [x for x in path.level]
            path_list.sort(key=lambda t: t[1])
            callNonTerm = []
            for i in range(len(path_list) - 1):
                first_rsa = path_list[i][0] // self.graph_size
                second_rsa = path_list[i + 1][0] // self.graph_size

                first_graph = path_list[i][0] % self.graph_size
                second_graph = path_list[i + 1][0] % self.graph_size

                for label in self.rsa.S():
                    if (first_rsa, second_rsa) in self.rsa.automaton()[label] and (current_len - path.level.nvals + 1 > 0):
                        callNonTerm.append([first_graph, second_graph, label])

            if len(callNonTerm) > 0:
                for call in callNonTerm:
                    sub_path = self.get_paths(call[0], call[1], call[2], current_len - path.level.nvals + 1)
                    if len(sub_path) != 0:
                        result_paths.append(path)
                        result_paths.extend(sub_path)
            else:
                result_paths.append(path)

        return result_paths
