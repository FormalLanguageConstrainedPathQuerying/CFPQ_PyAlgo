from src.grammar.cnf_grammar import CnfGrammar
from src.graph.index_graph import *


def matrix_single_path_algo(g: IndexGraph, grammar: CnfGrammar):
    IndexType_monoid = INDEXTYPE.new_monoid(INDEXTYPE.PLUS, INDEXTYPE.one)
    IndexType_semiring = INDEXTYPE.new_semiring(IndexType_monoid, INDEXTYPE.TIMES)
    with IndexType_semiring, INDEXTYPE.PLUS:
        m = IndexGraph()
        for l, r in grammar.simple_rules:
                m[l] += g[r]
        changed = True
        while changed:
            changed = False
            for l, r1, r2 in grammar.complex_rules:
                old_nnz = m[l].nvals
                m[l] += m[r1] @ m[r2]
                new_nnz = m[l].nvals
                if not old_nnz == new_nnz:
                    changed = True
        return m

class matrix_path:
    def __init__(self):
        self.length = 0
    def matrix_get_single_path(self, m: IndexGraph, grammar: CnfGrammar, i, j, s):
        def is_identity(lft, r, mid, h, lng):
            return lft == 0 and r == 0 and mid == 0 and h == 0 and lng == 0

        left, right, middle, height, length = m[s].get(i, j)
        if is_identity(left, right, middle, height, length):
            print("Index isn`t correct\n")

        if height == 1:
            self.length += 1
            #print("({0}-[:{1}]->{2})".format(left, s, right))
            #return new_length

        for l, r1, r2 in grammar.complex_rules:
            if s == l:
                #print(m[r1].get(left, middle))
                #print(r1)
                #print(left)
                #print(right)
                #print(r2)
                left_r1, right_r1, middle_r1, height_r1, length_r1 = 0, 0, 0, 0, 0
                if (left, middle) in m[r1]:
                    left_r1, right_r1, middle_r1, height_r1, length_r1 = m[r1].get(left, middle)
                left_r2, right_r2, middle_r2, height_r2, length_r2 = 0, 0, 0, 0, 0
                if (middle, right) in m[r2]:
                    left_r2, right_r2, middle_r2, height_r2, length_r2 = m[r2].get(middle, right)

                if not is_identity(left_r1, right_r1, middle_r1, height_r1, length_r1) and \
                        not is_identity(left_r2, right_r2, middle_r2, height_r2, length_r2):
                    max_height = height_r2 if height_r1 < height_r2 else height_r1
                    if height == max_height + 1:
                        self.matrix_get_single_path(m, grammar, left, middle, r1)
                        self.matrix_get_single_path(m, grammar, middle, right, r2)
                        break
