from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL

from pathlib import Path


class RecursiveAutomaton:
    """
    This class representing recursive state automaton. supports only the functions necessary for the algorithms to work
    """
    def __init__(self):
        self.labels = set()
        self.nonterminals = set()
        self.matrices = dict()
        self.states = dict()
        self.start_and_finish = set()
        self.matrices_size = 0
        self.start_state = dict()
        self.finish_states = dict()
        self.terminals = set()
        self.out_states = dict()

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(BOOL, self.matrices_size, self.matrices_size)

        return self.matrices[item]

    @classmethod
    def from_file(cls, path: Path):
        """
        Load RSA from file
        @param path: path to file with RSA
        @return: initialized class
        """
        rsa = RecursiveAutomaton()
        with open(path, "r") as file:
            count_matrix = int(file.readline())
            count_nonterminals = int(file.readline())
            matrices_size = int(file.readline())
            rsa.matrices_size = matrices_size

            for i in range(count_matrix):
                label = file.readline().replace("\n", "")
                rsa.labels.add(label)
                count_edge = int(file.readline())
                for j in range(count_edge):
                    first, second = file.readline().split()
                    rsa[label][int(first), int(second)] = True

                    if int(first) in rsa.out_states:
                        rsa.out_states[int(first)].append((int(second), label))
                    else:
                        rsa.out_states[int(first)] = [(int(second), label)]

            for i in range(count_nonterminals):
                label = file.readline().replace("\n", "")
                rsa.nonterminals.add(label)
                rsa.states.update({label: Matrix.sparse(BOOL, rsa.matrices_size, rsa.matrices_size)})
                count_edge = int(file.readline())
                for j in range(count_edge):
                    first, second = file.readline().split()
                    rsa.states[label][int(first), int(second)] = True
                    rsa.start_state.update({label: int(first)})
                    if label in rsa.finish_states:
                        rsa.finish_states[label].append(int(second))
                    else:
                        rsa.finish_states.update({label: [int(second)]})
                    if first == second:
                        rsa.start_and_finish.add(label)
        rsa.terminals = rsa.labels.difference(rsa.nonterminals)
        return rsa
