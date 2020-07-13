from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL


class RecursiveAutomaton:
    def __init__(self):
        self._labels = set()
        self._S = set()
        self._automaton = dict()
        self._states = dict()
        self._matrices_size = 0
        self._count_s = 0
        self._count_automaton = 0

    def labels(self):
        return self._labels

    def S(self):
        return self._S

    def automaton(self):
        return self._automaton

    def matrices_size(self):
        return self._matrices_size

    def count_s(self):
        return self._count_s

    def count_automaton(self):
        return self._count_automaton

    def states(self):
        return self._states

    def change_size(self, new_size: int):
        if new_size < 0:
            raise Exception("new size of matrix should be >= 0")
        self._matrices_size = new_size

    def change_count_s(self, new_count: int):
        if new_count < 0:
            raise Exception("new count of Snonterminals should be >= 0")
        self._count_s = new_count

    def change_count_matrix(self, new_count: int):
        if new_count < 0:
            raise Exception("new count of matrices should be >= 0")
        self._count_automaton = new_count

    def add_automaton(self, label: str):
        self._labels.add(label)
        self._automaton.update({label: Matrix.sparse(BOOL, self._matrices_size, self._matrices_size)})

    def add_states(self, label: str):
        self._S.add(label)
        self._states.update({label: Matrix.sparse(BOOL, self._matrices_size, self._matrices_size)})

    def from_file(self, path: str):
        with open(path, "r") as file:
            count_matrix = int(file.readline())
            self.change_count_matrix(count_matrix)
            count_s = int(file.readline())
            self.change_count_s(count_s)
            size_matrix = int(file.readline())
            self.change_size(size_matrix)

            for i in range(count_matrix):
                label = file.readline().replace("\n", "")
                self.add_automaton(label)
                count_edge = int(file.readline())
                for j in range(count_edge):
                    first, second = file.readline().split()
                    self._automaton[label][int(first), int(second)] = True

            for i in range(count_s):
                label = file.readline().replace("\n", "")
                self.add_states(label)
                count_edge = int(file.readline())
                for j in range(count_edge):
                    first, second = file.readline().split()
                    self._states[label][int(first), int(second)] = True
