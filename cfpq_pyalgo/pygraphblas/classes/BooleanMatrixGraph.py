from pygraphblas import Matrix, BOOL

__all__ = [
    "BooleanMatrixGraph",
]


class BooleanMatrixGraph:
    def __init__(self, matrices_size: int):
        self.matrices_size = matrices_size
        self.matrices = dict()

    def __getitem__(self, item) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(BOOL, self.matrices_size, self.matrices_size)
        return self.matrices[item]

    def __setitem__(self, key, value: Matrix):
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()
