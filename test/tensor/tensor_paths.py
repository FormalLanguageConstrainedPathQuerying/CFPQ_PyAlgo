import unittest

from src.algo.tensor_path import TensorPaths
from src.grammar.rsa import RecursiveAutomaton
from src.algo.tensor import tensor_algo
from src.graph.label_graph import LabelGraph


class MyTestCase(unittest.TestCase):
    def test_simple(self):
        graph = LabelGraph.from_txt("../suites/data/tensor/test_simple/graph_simple")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_simple")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths_1 = TensorPaths(rsa, graph_res, tc, 1)
        result_1 = paths_1.GetPaths(0, 2, "S")
        self.assertEqual([[[0, 1], [1, 2]]], result_1.paths)

        paths_2 = TensorPaths(rsa, graph_res, tc, 1)
        result_2 = paths_2.GetPaths(2, 4, "S")
        self.assertEqual([[[2, 3], [3, 4]]], result_2.paths)

    def test_cycle(self):
        graph = LabelGraph.from_txt("../suites/data/tensor/test_cycle/graph_cycle")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_cycle")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths = TensorPaths(rsa, graph_res, tc, 1)
        result = paths.GetPaths(0, 0, "S")
        self.assertEqual([[[0, 1], [1, 2], [2, 0]]], result.paths)

    def test_rpq(self):
        graph = LabelGraph.from_txt("../suites/data/tensor/test_rpq/graph_rpq")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_rpq")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths_1 = TensorPaths(rsa, graph_res, tc, 1)
        result = paths_1.GetPaths(0, 5, "S")
        self.assertEqual([[[0, 1], [1, 4], [4, 5]]], result.paths)

        paths_2 = TensorPaths(rsa, graph_res, tc, 1)
        result = paths_2.GetPaths(1, 3, "S")
        self.assertEqual([[[1, 2], [2, 3]]], result.paths)

    def test_one_edge(self):
        graph = LabelGraph.from_txt("../suites/data/tensor/test_rpq/graph_rpq")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_rpq")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths = TensorPaths(rsa, graph_res, tc, 1)
        result = paths.GetPaths(0, 1, "S")
        self.assertEqual([[[0, 1]]], result.paths)

    def test_loop(self):
        graph = LabelGraph.from_txt("../suites/data/tensor/test_loop/graph_loop")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_loop")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths = TensorPaths(rsa, graph_res, tc, 1)
        result = paths.GetPaths(0, 0, "S")
        self.assertEqual([[[0, 0]]], result.paths)

    def test_count_paths(self):
        graph = LabelGraph.from_txt("graph_paths")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_paths")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths_3 = TensorPaths(rsa, graph_res, tc, 3)
        result = paths_3.GetPaths(0, 2, "S")
        self.assertEqual([[[0, 3], [3, 2]], [[0, 4], [4, 2]], [[0, 1], [1, 2]]], result.paths)

        paths_2 = TensorPaths(rsa, graph_res, tc, 2)
        result = paths_2.GetPaths(0, 2, "S")
        if [[0, 1], [1, 2]] in result.paths and [[0, 3], [3, 2]] in result.paths:
            self.assertEqual([[[0, 1], [1, 2]], [[0, 3], [3, 2]]], result.paths)
        if [[0, 1], [1, 2]] in result.paths and [[0, 4], [4, 2]] in result.paths:
            self.assertEqual([[[0, 1], [1, 2]], [[0, 4], [4, 2]]], result.paths)
        if [[0, 3], [3, 2]] in result.paths and [[0, 4], [4, 2]] in result.paths:
            self.assertEqual([[[0, 3], [3, 2]], [[0, 4], [4, 2]]], result.paths)

        paths_1 = TensorPaths(rsa, graph_res, tc, 1)
        result = paths_1.GetPaths(0, 2, "S")
        if [[0, 1], [1, 2]] in result.paths:
            self.assertEqual([[[0, 1], [1, 2]]], result.paths)
        if [[0, 3], [3, 2]] in result.paths:
            self.assertEqual([[[0, 3], [3, 2]]], result.paths)
        if [[0, 4], [4, 2]] in result.paths:
            self.assertEqual([[[0, 4], [4, 2]]], result.paths)


if __name__ == '__main__':
    unittest.main()
