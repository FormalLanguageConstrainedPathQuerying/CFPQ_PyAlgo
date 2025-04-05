from abc import ABC, abstractmethod
from typing import Tuple

from graphblas.core.matrix import Matrix

class Decomposer(ABC):
    @abstractmethod
    def decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        """
        Decomposes a sparse boolean matrix M into LEFT, RIGHT such that
        for all i,j : M[i,j] >= (LEFT * RIGHT)[i, j].

        Parameters:
        M (gb.Matrix): Input sparse boolean matrix.

        Returns:
        LEFT (gb.Matrix): Left factor matrix.
        RIGHT (gb.Matrix): Right factor matrix.
        """