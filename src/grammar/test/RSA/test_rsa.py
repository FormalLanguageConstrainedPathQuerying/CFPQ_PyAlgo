import unittest
from src.grammar.rsa import RecursiveAutomaton


class TestRSA(unittest.TestCase):
    def test_load(self):
        rsa = RecursiveAutomaton()
        rsa.from_file("ex1")

        self.assertEqual(len(rsa.labels()), 1)
        self.assertEqual(rsa.labels(), {"18"})
        self.assertEqual(len(rsa.states()), 1)
        self.assertEqual(rsa.count_s(), 1)
        self.assertEqual(rsa.S(), {"S"})
        self.assertEqual(rsa.count_automaton(), 1)
        self.assertEqual(rsa.matrices_size(), 1)

        rsa = RecursiveAutomaton()
        rsa.from_file("ex2")

        self.assertEqual(len(rsa.labels()), 2)
        self.assertEqual(len(rsa.states()), 1)
        self.assertEqual(rsa.count_s(), 1)
        self.assertEqual(rsa.count_automaton(), 2)
        self.assertEqual(rsa.matrices_size(), 3)

        rsa = RecursiveAutomaton()
        rsa.from_file("ex3")

        self.assertEqual(len(rsa.labels()), 6)
        self.assertEqual(len(rsa.states()), 2)
        self.assertEqual(rsa.count_s(), 2)
        self.assertEqual(rsa.count_automaton(), 6)
        self.assertEqual(rsa.matrices_size(), 8)



if __name__ == '__main__':
    unittest.main()
