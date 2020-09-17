from pygraphblas import Matrix
from more_itertools import unique_everseen

from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph


def get_elements(s: set, n):
    count = 0
    result = set()
    for elem in s:
        if count == n:
            break
        result.add(elem)
        count += 1

    return result


class Paths:

    def __init__(self):
        self.paths = []
        self.path_start = dict()
        self.path_end = dict()

    def add_one_edge(self, path):
        self.paths.append([path])

        self.path_end.update({len(self.paths) - 1: path[1]})

        try:
            self.path_start[path[0]].append(len(self.paths) - 1)
        except KeyError:
            self.path_start.update({path[0]: [len(self.paths) - 1]})

    def union_paths(self, second):

        if len(second.paths) == 0:
            return

        for i in range(len(second.paths)):
            self.path_end.update({len(self.paths) + i: second.path_end[i]})
        for start in second.path_start:
            second.path_start.update({start: [i + len(self.paths) for i in second.path_start[start]]})

            if start in self.path_start:
                self.path_start[start].extend(second.path_start[start])
            else:
                self.path_start.update({start: second.path_start[start]})

        self.paths.extend(second.paths)

    def clean_paths(self):
        self.paths.clear()

    def doSet(self):
        self.paths = list(unique_everseen(self.paths, key=tuple))

    def product_paths(self, right):

        if not self.paths:
            for path_r in right.paths:
                self.paths.append(path_r)

            self.path_end = right.path_end
            self.path_start = right.path_start
            right.clean_paths()

        if self.paths and right.paths:
            for pos_l in self.path_end:
                if self.path_end[pos_l] in right.path_start:
                    for pos_r in right.path_start[self.path_end[pos_l]]:
                        self.paths[pos_l].extend(right.paths[pos_r])
                        self.path_end.update({pos_l: right.path_end[pos_r]})


class TensorPaths:

    def __init__(self, rsa: RecursiveAutomaton, graph: LabelGraph, tc: Matrix, count_paths):
        self.rsa = rsa
        self.size_graph = graph.matrices_size

        self.exist_paths = set()
        self.exist_inner = set()

        self.count_paths = count_paths
        self.last_count = 1

        self.last_inner = (-1, -1)

        self.tc = tc

        self.rsa_element = dict()
        for label in rsa.labels():
            self.rsa_element.update({label: {(i[0], i[1]) for i in rsa.automaton()[label]}})

        self.graph_element = graph

    def new_launch(self):
        self.exist_inner = set()
        self.exist_inner = set()
        self.last_count = 1
        self.last_inner = (-1, -1)

    def GetPaths(self, v_s, v_f, N):

        if (v_s, v_f) in self.exist_paths:
            return Paths()

        #print("Get paths (" + str(v_s) + ", " + str(v_f) + ")")

        self.exist_paths.add((v_s, v_f))

        q_N = self.rsa.start_state()[N]
        f_N = self.rsa.finish_states()[N]

        result = Paths()
        for f in f_N:

            check = True
            for label in self.rsa.labels().difference(self.rsa.S()):
                if (v_s, v_f) in self.graph_element[label] and (q_N, f) in self.rsa_element[label]:
                    result.add_one_edge([v_s, v_f])
                    if self.count_paths == 1:
                        check = False
            if check:
                result.union_paths(self.GetPathsInner(q_N * self.size_graph + v_s, f * self.size_graph + v_f))

        self.exist_paths.remove((v_s, v_f))

        #print("Get paths (" + str(v_s) + ", " + str(v_f) + ")")
        #print("result = " + str(result))

        if not self.exist_paths:
            result.doSet()

        return result

    def GetPathsInner(self, i, j):

        #print("Get paths inner (" + str(i) + ", " + str(j) + ")")

        if (i, j) in self.exist_inner:
            return Paths()

        self.exist_inner.add((i, j))

        #parts = set()

        parts = self.tc[i] * self.tc[:, j]

        if parts.nvals > 1:
            dif = self.count_paths - parts.nvals + 1 - self.last_count
            if dif >= 0:
                self.last_count += parts.nvals - 1
            else:
                parts = get_elements(parts, parts.nvals + dif)

        result = Paths()
        for part in parts:
            result.union_paths(self.GetSubPaths(i, j, part[0]))

        self.exist_inner.remove((i, j))

        #print("Get paths inner (" + str(i) + ", " + str(j) + ")")
        #print("result = " + str(result))

        return result

    def GetSubPaths(self, i, j, k):
        #print("get sub paths (" + str(i) + ", " + str(j) + ", " + str(k) + ")")

        left = Paths()
        for label in self.rsa.labels().difference(self.rsa.S()):
            if (i % self.size_graph, k % self.size_graph) in self.graph_element[label] and (
                    i // self.size_graph, k // self.size_graph) in self.rsa_element[label]:
                left.add_one_edge([i % self.size_graph,  k % self.size_graph])

        for N in self.rsa.S():
            if N not in self.rsa_element:
                continue
            if (i // self.size_graph, k // self.size_graph) in self.rsa_element[N]:
                left.union_paths(self.GetPaths(i % self.size_graph, k % self.size_graph, N))

        left.union_paths(self.GetPathsInner(i, k))

        #print("get sub paths (" + str(i) + ", " + str(j) + ", " + str(k) + ")")
        #print("left = " + str(left))

        right = Paths()
        for label in self.rsa.labels().difference(self.rsa.S()):
            if (k % self.size_graph, j % self.size_graph) in self.graph_element[label] and (
                    k // self.size_graph, j // self.size_graph) in self.rsa_element[label]:
                right.add_one_edge([k % self.size_graph,  j % self.size_graph])

        for N in self.rsa.S():
            if N not in self.rsa_element:
                continue
            if (k // self.size_graph, j // self.size_graph) in self.rsa_element[N]:
                right.union_paths(self.GetPaths(k % self.size_graph, j % self.size_graph, N))

        right.union_paths(self.GetPathsInner(k, j))

        #print("get sub paths (" + str(i) + ", " + str(j) + ", " + str(k) + ")")
        #print("right = " + str(right))

        left.product_paths(right)

        return left
