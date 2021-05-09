from pygraphblas import Matrix

from src.graph.label_graph import LabelGraph
from src.grammar.rsa import RecursiveAutomaton


class Paths:
    def __init__(self, path, current_vertex):
        self.path = path
        self.current_vertex = current_vertex
        self.use = True

    def close(self):
        self.use = False


class TensorPaths:
    def __init__(self, graph: LabelGraph, rsa: RecursiveAutomaton, tc: Matrix):
        self.graph = graph
        self.rsa = rsa
        self.tc = tc
        self.graph_size = graph.matrices_size

    def gen_paths(self, i, j, max_len):
        first_path = Paths([i], i)
        supposed_paths = [first_path]
        result_paths = []
        for current_len in range(max_len - 1):
            current_size = len(supposed_paths)
            for i in range(current_size):
                if not supposed_paths[i].use:
                    continue

                first_iter = True
                current_vertex = supposed_paths[i].current_vertex
                copy_paths = supposed_paths[i].path.copy()
                for new_vertex in self.tc[current_vertex]:
                    if first_iter:
                        supposed_paths[i].path.append(new_vertex[0])
                        supposed_paths[i].current_vertex = new_vertex[0]
                        first_iter = False
                        if new_vertex[0] == j:
                            result_paths.append(supposed_paths[i].path.copy())
                    else:
                        new_path = copy_paths.copy()
                        new_path.append(new_vertex[0])
                        supposed_paths.append(Paths(new_path, new_vertex[0]))
                        if new_vertex[0] == j:
                            result_paths.append(supposed_paths[-1].path.copy())

                if first_iter:
                    supposed_paths[i].close()

        return result_paths

    def get_paths(self, start, finish, nonterm, max_len):
        if max_len <= 0:
            return []

        supposed_paths = []
        for finish_state in self.rsa.finish_states[nonterm]:
            supposed_paths += self.gen_paths(self.rsa.start_state[nonterm] * self.graph_size + start,
                                            finish_state * self.graph_size + finish, max_len)

        result_paths = []
        for path in supposed_paths:
            callNonterm = []
            current_size = 0
            for i in range(len(path) - 1):
                first_rsa = path[i] // self.graph_size
                second_rsa = path[i + 1] // self.graph_size

                first_graph = path[i] % self.graph_size
                second_graph = path[i + 1] % self.graph_size

                check = False
                for label in self.rsa.nonterminals:
                    if (first_rsa, second_rsa) in self.rsa[label]:
                        callNonterm.append([first_graph, second_graph, label])
                        check = True

                if not check:
                    current_size += 1

            if len(callNonterm) > 0:
                min_size = current_size
                construct_paths = [current_size]
                stop = False
                for call in callNonterm:
                    sub_paths = self.get_paths(call[0], call[1], call[2], max_len - min_size - len(callNonterm) + 1)
                    if len(sub_paths) == 0:
                        stop = True
                        break

                    first_iter = True
                    new_min = 0
                    new_construct_paths = []
                    for constr_path in construct_paths:
                        for sub_path in sub_paths:
                            if constr_path + sub_path < max_len:
                                if first_iter:
                                    new_min = constr_path + sub_path
                                else:
                                    if constr_path + sub_path < new_min:
                                        new_min = constr_path + sub_path
                                new_construct_paths.append(constr_path + sub_path)

                    min_size = new_min
                    construct_paths = new_construct_paths

                if not stop:
                    result_paths.extend(construct_paths)

            else:
                result_paths.append(current_size)

        return result_paths
