from src.grammar.cnf_grammar import CnfGrammar
from src.graph.index_graph import IndexGraph


class MatrixSinglePath:
    def __init__(self, graph: IndexGraph, grammar: CnfGrammar):
        self.length = 0
        self.m = graph
        self.grammar = grammar

    def get_path(self, i, j, s):
        def is_identity(lft, r, mid, h, lng):
            return lft == 0 and r == 0 and mid == 0 and h == 0 and lng == 0

        left, right, middle, height, length = self.m[s].get(i, j)
        if is_identity(left, right, middle, height, length):
            print("Index isn`t correct\n")

        if height == 1:
            self.length += 1

        for l, r1, r2 in self.grammar.complex_rules:
            if s == l:
                left_r1, right_r1, middle_r1, height_r1, length_r1 = 0, 0, 0, 0, 0
                if (left, middle) in self.m[r1]:
                    left_r1, right_r1, middle_r1, height_r1, length_r1 = self.m[r1].get(left, middle)
                left_r2, right_r2, middle_r2, height_r2, length_r2 = 0, 0, 0, 0, 0
                if (middle, right) in self.m[r2]:
                    left_r2, right_r2, middle_r2, height_r2, length_r2 = self.m[r2].get(middle, right)

                if not is_identity(left_r1, right_r1, middle_r1, height_r1, length_r1) and \
                        not is_identity(left_r2, right_r2, middle_r2, height_r2, length_r2):
                    max_height = height_r2 if height_r1 < height_r2 else height_r1
                    if height == max_height + 1:
                        self.get_path(left, middle, r1)
                        self.get_path(middle, right, r2)
                        break

        return self.length
