from pygraphblas import Matrix


class ResultAlgo:
    def __init__(self, matrix_S: Matrix, iter: int):
        self.matrix_S = matrix_S
        self.number_iter = iter
