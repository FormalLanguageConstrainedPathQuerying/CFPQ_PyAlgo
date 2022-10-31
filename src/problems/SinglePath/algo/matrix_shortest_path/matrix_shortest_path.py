from src.grammar.cnf_grammar import CnfGrammar
from src.graph.length_graph import LengthGraph
from src.graph.length_graph import MAX_MATRIX_SIZE


class MatrixShortestPath:
    def __init__(self, graph: LengthGraph, grammar: CnfGrammar):
        self.length = 0
        self.m = graph
        self.grammar = grammar

    def get_path(self, i, j, s):
        def is_identity(lft, r, mid, lng):
            return lft == 0 and r == 0 and mid == 0 and lng == MAX_MATRIX_SIZE

        left, right, middle, length = self.m[s].get(i, j)
        if is_identity(left, right, middle, length):
            print("Index isn`t correct\n")

        if length == 1:
            self.length += 1  # edges can be stored here

        for l, r1, r2 in self.grammar.complex_rules:
            if s == l:
                left_r1, right_r1, middle_r1, length_r1 = 0, 0, 0, MAX_MATRIX_SIZE
                if (left, middle) in self.m[r1]:
                    left_r1, right_r1, middle_r1, length_r1 = self.m[r1].get(left, middle)
                left_r2, right_r2, middle_r2, length_r2 = 0, 0, 0, MAX_MATRIX_SIZE
                if (middle, right) in self.m[r2]:
                    left_r2, right_r2, middle_r2, length_r2 = self.m[r2].get(middle, right)

                if not is_identity(left_r1, right_r1, middle_r1, length_r1) and \
                        not is_identity(left_r2, right_r2, middle_r2, length_r2):
                    if length == length_r1 + length_r2:
                        self.get_path(left, middle, r1)
                        self.get_path(middle, right, r2)
                        break

        return self.length
