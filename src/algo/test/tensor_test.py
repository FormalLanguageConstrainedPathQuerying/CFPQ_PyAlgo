import unittest

from src.algo.tensor import tensor_algo
from src.grammar.rsa import RecursiveAutomaton
from cfpq_data_devtools.data_wrapper import DataWrapper
from src.graph.label_graph import LabelGraph


class Test_tensor(unittest.TestCase):
    def test_fullgraph(self):
        graphs = DataWrapper("/home/ilya/CFPQ_PyAlgo/deps/CFPQ_Data/data").get_graphs("FullGraph",
                                                                                      include_extensions="txt")
        grammar = RecursiveAutomaton()
        grammar.from_file("/home/ilya/CFPQ_PyAlgo/src/grammar/test/RSA/ex2")
        sums = list()

        print(graphs)

        for path_graph in graphs:
            graph = LabelGraph.from_txt(path_graph)
            sums.append(tensor_algo(graph, grammar))

        print(sums)

        self.assertEqual(sums[1], 10000)
        self.assertEqual(sums[0], 40000)
        self.assertEqual(sums[2], 1000000)

    def test_worstcase(self):
        graphs = DataWrapper("/home/ilya/CFPQ_PyAlgo/deps/CFPQ_Data/data").get_graphs("WorstCase",
                                                                                      include_extensions="txt")

        grammar = RecursiveAutomaton()
        grammar.from_file("/home/ilya/CFPQ_PyAlgo/src/grammar/test/RSA/ex_w")
        sums = list()

        print(graphs)

        for path_graph in graphs:
            graph = LabelGraph.from_txt(path_graph)
            sums.append(tensor_algo(graph, grammar))

        print(sums)

        self.assertEqual(sums[1], 272)
        self.assertEqual(sums[0], 65792)
        self.assertEqual(sums[2], 4160)

    def test_RDF(self):
        graphs = DataWrapper("/home/ilya/CFPQ_PyAlgo/deps/CFPQ_Data/data").get_graphs("RDF",
                                                                                      include_extensions="txt")

        grammar = RecursiveAutomaton()
        grammar.from_file("/home/ilya/CFPQ_PyAlgo/src/grammar/test/RSA/ex_w")
        sums = list()

        print(graphs)

        for path_graph in graphs:
            graph = LabelGraph.from_txt(path_graph)
            sums.append(tensor_algo(graph, grammar))

        print(sums)

        self.assertEqual(sums[1], 272)
        self.assertEqual(sums[0], 65792)
        self.assertEqual(sums[2], 4160)


if __name__ == '__main__':
    unittest.main()
