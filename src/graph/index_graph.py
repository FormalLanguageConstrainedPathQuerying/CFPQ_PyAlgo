from pygraphblas import Matrix
from pygraphblas.types import Type, binop

MAX_MATRIX_SIZE = 10000000


class SAVEMIDDLETYPE(Type):
    _base_name = "UDT"
    members = ['uint32_t left', 'uint32_t right', 'uint32_t middle', 'uint32_t height', 'uint32_t length']
    one = (0, 0, 0, 0, 0)

    @binop(boolean=True)
    def EQ(z, x, y):
        if x.left == y.left and x.right == y.right and x.middle == y.middle and x.height == y.height \
                and x.length == y.length:
            z = True
        else:
            z = False

    @binop()
    def PLUS(z, x, y):
        def is_eq_to_one(ind):
            return ind.left == 0 and ind.right == 0 and ind.middle == 0 and ind.height == 0 and ind.length == 0

        if not is_eq_to_one(x) and not is_eq_to_one(y):
            min_height_index = x if x.height < y.height else y
            z.left = min_height_index.left
            z.right = min_height_index.right
            z.middle = min_height_index.middle
            z.height = min_height_index.height
            z.length = min_height_index.length
        elif is_eq_to_one(x):
            z.left = y.left
            z.right = y.right
            z.middle = y.middle
            z.height = y.height
            z.length = y.length
        else:
            z.left = x.left
            z.right = x.right
            z.middle = x.middle
            z.height = x.height
            z.length = x.length

    @binop()
    def TIMES(z, x, y):
        def is_eq_to_one(ind):
            return ind.left == 0 and ind.right == 0 and ind.middle == 0 and ind.height == 0 and ind.length == 0

        if not is_eq_to_one(x) and not is_eq_to_one(y):
            z.left = x.left
            z.right = y.right
            z.middle = x.right
            z.height = (y.height if x.height < y.height else x.height) + 1
            z.length = x.length + y.length
        else:
            z.left = 0
            z.right = 0
            z.middle = 0
            z.height = 0
            z.length = 0


class IndexGraph:
    def __init__(self, matrices_size=MAX_MATRIX_SIZE):
        self.matrices = {}
        self.matrices_size = matrices_size

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(SAVEMIDDLETYPE, self.matrices_size, self.matrices_size)
        return self.matrices[item]

    def __setitem__(self, key, value):
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()

    @classmethod
    def from_txt(cls, path):
        g = IndexGraph()
        with open(path, 'r') as f:
            for line in f.readlines():
                v, label, to = line.split()
                v, to = int(v), int(to)
                g[label][v, to] = (v, to, v, 1, 1)
        return g
