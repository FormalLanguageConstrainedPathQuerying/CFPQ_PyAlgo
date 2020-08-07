import unittest

from src.algo.tensor_path import TensorPaths
from src.grammar.rsa import RecursiveAutomaton
from src.algo.tensor import tensor_algo
from src.graph.label_graph import LabelGraph


class MyTestCase(unittest.TestCase):
    def test_simple(self):
        graph = LabelGraph.from_txt("graph_simple")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_simple")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths_1 = TensorPaths(rsa, graph_res, tc, 1)
        result_1 = paths_1.GetPaths(0, 2, "S")
        self.assertEqual({(0, "a", 1, "b", 2)}, result_1)

        paths_2 = TensorPaths(rsa, graph_res, tc, 1)
        result_2 = paths_2.GetPaths(2, 4, "S")
        self.assertEqual({(2, "a", 3, "b", 4)}, result_2)

    def test_cycle(self):
        graph = LabelGraph.from_txt("graph_cycle")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_cycle")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths = TensorPaths(rsa, graph_res, tc, 1)
        result = paths.GetPaths(0, 0, "S")
        self.assertEqual({(0, "A", 1, "A", 2, "A", 0)}, result)

    def test_rpq(self):
        graph = LabelGraph.from_txt("graph_rpq")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_rpq")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths_1 = TensorPaths(rsa, graph_res, tc, 1)
        result = paths_1.GetPaths(0, 5, "S")
        self.assertEqual({(0, "a", 1, "b", 4, "b", 5)}, result)

        paths_2 = TensorPaths(rsa, graph_res, tc, 1)
        result = paths_2.GetPaths(1, 3, "S")
        self.assertEqual({(1, "a", 2, "b", 3)}, result)

    def test_one_edge(self):
        graph = LabelGraph.from_txt("graph_rpq")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_rpq")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths = TensorPaths(rsa, graph_res, tc, 1)
        result = paths.GetPaths(0, 1, "S")
        self.assertEqual({(0, "a", 1)}, result)

    def test_loop(self):
        graph = LabelGraph.from_txt("graph_loop")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_loop")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths = TensorPaths(rsa, graph_res, tc, 1)
        result = paths.GetPaths(0, 0, "S")
        self.assertEqual({(0, "a", 0)}, result)

    def test_count_paths(self):
        graph = LabelGraph.from_txt("graph_paths")
        rsa = RecursiveAutomaton()
        rsa.from_file("rsa_paths")
        _, graph_res, tc = tensor_algo(graph, rsa)

        paths_3 = TensorPaths(rsa, graph_res, tc, 3)
        result = paths_3.GetPaths(0, 2, "S")
        self.assertEqual({(0, "a", 1, "b", 2), (0, "a", 3, "b", 2), (0, "a", 4, "b", 2)}, result)

        paths_2 = TensorPaths(rsa, graph_res, tc, 2)
        result = paths_2.GetPaths(0, 2, "S")
        if (0, "a", 1, "b", 2) in result and (0, "a", 3, "b", 2) in result:
            self.assertEqual({(0, "a", 1, "b", 2), (0, "a", 3, "b", 2)}, result)
        if (0, "a", 1, "b", 2) in result and (0, "a", 4, "b", 2) in result:
            self.assertEqual({(0, "a", 1, "b", 2), (0, "a", 4, "b", 2)}, result)
        if (0, "a", 3, "b", 2) in result and (0, "a", 4, "b", 2) in result:
            self.assertEqual({(0, "a", 3, "b", 2), (0, "a", 4, "b", 2)} ,result)

        paths_1 = TensorPaths(rsa, graph_res, tc, 1)
        result = paths_1.GetPaths(0, 2, "S")
        if (0, "a", 1, "b", 2) in result:
            self.assertEqual({(0, "a", 1, "b", 2)}, result)
        if (0, "a", 3, "b", 2) in result:
            self.assertEqual({(0, "a", 3, "b", 2)}, result)
        if (0, "a", 4, "b", 2) in result:
            self.assertEqual({(0, "a", 4, "b", 2)}, result)


if __name__ == '__main__':
    unittest.main()
