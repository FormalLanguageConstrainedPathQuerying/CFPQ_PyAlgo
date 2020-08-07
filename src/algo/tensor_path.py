from pygraphblas import Matrix

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


class TensorPaths:
    def __init__(self, rsa: RecursiveAutomaton, graph: LabelGraph, tc: Matrix, count_paths):
        self.rsa = rsa
        self.size_graph = graph.matrices_size

        self.exist = set()

        self.count_paths = count_paths
        self.last_count = 1

        self.last_inner = (-1, -1)

        self.tc = tc

        self.tc_coord = {i[0] for i in tc}
        for i in tc:
            self.tc_coord.add(i[1])

        self.rsa_element = dict()
        for label in rsa.labels():
            self.rsa_element.update({label: {(i[0], i[1]) for i in rsa.automaton()[label]}})

        self.graph_element = dict()
        for label in graph:
            self.graph_element.update({label: {(i[0], i[1]) for i in graph[label]}})

    def product_paths(self, left, right):

        #print("Product paths: l = " + str(left) + "   r = " + str(right))

        result = set()

        if not left:
            for path_r in right:
                result.add(path_r)
            right.clear()

        if not right:
            for path_l in left:
                result.add(path_l)
            left.clear()

        if left and right:
            new_right = set()
            for path_l in left:
                check = False
                for path_r in right:
                    if path_l[-1] == path_r[0]:
                        new_path = path_l[:-1] + path_r
                        result.add(new_path)
                        check = True
                        new_right.add(path_r)

                if not check:
                    result.add(path_l)
            right.difference_update(new_right)
            for path in right:
                result.add(path)

        #print("result = " + str(result))

        return result

    def GetPaths(self, v_s, v_f, N):

        if (v_s, v_f) in self.exist:
            return set()

        #print("Get paths (" + str(v_s) + ", " + str(v_f) + ")")

        self.exist.add((v_s, v_f))

        q_N = self.rsa.start_state()[N]
        f_N = self.rsa.finish_states()[N]

        result = set()
        for f in f_N:

            check = True
            for label in self.rsa.labels().difference(self.rsa.S()):
                if (v_s, v_f) in self.graph_element[label] and (q_N, f) in self.rsa_element[label]:
                    result.add((v_s, v_f))
                    if self.count_paths == 1:
                        check = False
            if check:
                in_set = self.GetPathsInner(q_N * self.size_graph + v_s, f * self.size_graph + v_f)
                for path in in_set:
                    result.add(path)

        self.exist.remove((v_s, v_f))

        #print("Get paths (" + str(v_s) + ", " + str(v_f) + ")")
        #print("result = " + str(result))

        return result

    def GetPathsInner(self, i, j):

        #print("Get paths inner (" + str(i) + ", " + str(j) + ")")

        if (i, j) == self.last_inner:
            return set()
        else:
            self.last_inner = (i, j)

        parts = set()

        for elem in self.tc_coord:
            if (i, elem) in self.tc and (elem, j) in self.tc:
                parts.add(elem)

        if len(parts) > 1:
            dif = self.count_paths - len(parts) + 1 - self.last_count
            if dif >= 0:
                self.last_count += len(parts) - 1
            else:
                parts = get_elements(parts, len(parts) + dif)

        result = set()
        for part in parts:
            sub_set = self.GetSubPaths(i, j, part)
            for path in sub_set:
                result.add(path)

        #print("Get paths inner (" + str(i) + ", " + str(j) + ")")
        #print("result = " + str(result))

        return result

    def GetSubPaths(self, i, j, k):
        #print("get sub paths (" + str(i) + ", " + str(j) + ", " + str(k) + ")")

        left = set()
        for label in self.rsa.labels().difference(self.rsa.S()):
            if (i % self.size_graph, k % self.size_graph) in self.graph_element[label] and (
                    i // self.size_graph, k // self.size_graph) in self.rsa_element[label]:
                left.add((i % self.size_graph,  k % self.size_graph))

        for N in self.rsa.S():
            if N not in self.rsa_element:
                continue
            if (i // self.size_graph, k // self.size_graph) in self.rsa_element[N]:
                new_path = self.GetPaths(i % self.size_graph, k % self.size_graph, N)
                for path in new_path:
                    left.add(path)

        path_l = self.GetPathsInner(i, k)
        for path in path_l:
            left.add(path)

        #print("get sub paths (" + str(i) + ", " + str(j) + ", " + str(k) + ")")
        #print("left = " + str(left))

        right = set()
        for label in self.rsa.labels().difference(self.rsa.S()):
            if (k % self.size_graph, j % self.size_graph) in self.graph_element[label] and (
                    k // self.size_graph, j // self.size_graph) in self.rsa_element[label]:
                right.add((k % self.size_graph, j % self.size_graph))

        for N in self.rsa.S():
            if N not in self.rsa_element:
                continue
            if (k // self.size_graph, j // self.size_graph) in self.rsa_element[N]:
                new_path = self.GetPaths(k % self.size_graph, j % self.size_graph, N)
                for path in new_path:
                    right.add(path)

        path_r = self.GetPathsInner(k, j)
        for path in path_r:
            right.add(path)

        #print("get sub paths (" + str(i) + ", " + str(j) + ", " + str(k) + ")")
        #print("right = " + str(right))

        result = self.product_paths(left, right)

        return result
