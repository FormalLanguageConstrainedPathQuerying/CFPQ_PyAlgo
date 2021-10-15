from pygraphblas import *
from pygraphblas import Matrix
from pygraphblas.types import Type, binop
from pygraphblas.types import BOOL
import numpy as np

MAX_MATRIX_SIZE = 10000000
UINT32_MAX = np.iinfo(np.uint32).max


class SAVELENGTHTYPE(Type):
    _base_name = "UDT"
    _numpy_t = None
    members = ['uint32_t left', 'uint32_t right', 'uint32_t middle', 'uint32_t length']
    one = (0, 0, 0, UINT32_MAX)

    @binop(boolean=True)
    def EQ(z, x, y):
        if x.left == y.left and x.right == y.right and x.middle == y.middle and x.length == y.length:
            z = True
        else:
            z = False

    @binop()
    def PLUS(z, x, y):
        def is_eq_to_one(ind):
            return ind.left == 0 and ind.right == 0 and ind.middle == 0 and ind.length == UINT32_MAX

        if not is_eq_to_one(x) and not is_eq_to_one(y):
            min_length_index = x if x.length < y.length else y
            z.left = min_length_index.left
            z.right = min_length_index.right
            z.middle = min_length_index.middle
            z.length = min_length_index.length
        elif is_eq_to_one(x):
            z.left = y.left
            z.right = y.right
            z.middle = y.middle
            z.length = y.length
        else:
            z.left = x.left
            z.right = x.right
            z.middle = x.middle
            z.length = x.length

    @binop()
    def TIMES(z, x, y):
        def is_eq_to_one(ind):
            return ind.left == 0 and ind.right == 0 and ind.middle == 0 and ind.length == UINT32_MAX

        if not is_eq_to_one(x) and not is_eq_to_one(y):
            z.left = x.left
            z.right = y.right
            z.middle = x.right
            z.length = x.length + y.length
        else:
            z.left = 0
            z.right = 0
            z.middle = 0
            z.length = MAX_MATRIX_SIZE

    @binop()
    def SUBTRACTION(z, x, y):
        if x.left == y.left and x.right == y.right and x.middle == y.middle and x.length == y.length:
            z.left = 0
            z.right = 0
            z.middle = 0
            z.length = 0   # for nonzero() function and GxB_NONZERO select operator
        else:
            z.left = UINT32_MAX
            z.right = UINT32_MAX
            z.middle = UINT32_MAX
            z.length = UINT32_MAX


class LengthGraph:
    def __init__(self, matrices_size=MAX_MATRIX_SIZE):
        self.matrices = {}
        self.matrices_size = matrices_size

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(SAVELENGTHTYPE, self.matrices_size, self.matrices_size)
        return self.matrices[item]

    def __setitem__(self, key, value):
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()

    @classmethod
    def from_txt(cls, path):
        g = LengthGraph()
        with open(path, 'r') as f:
            for line in f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)
                g[label][v, to] = (v, to, v, 1)
        return g
