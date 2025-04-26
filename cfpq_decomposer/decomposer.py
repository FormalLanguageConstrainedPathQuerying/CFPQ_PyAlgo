from abc import ABC, abstractmethod
from typing import Tuple

from graphblas.core.matrix import Matrix

class Decomposer(ABC):
    @abstractmethod
    def decompose(self, matrix: Matrix) -> Tuple[Matrix, Matrix]:
        """
        Decomposes a sparse boolean matrix `matrix` into matrices
        `left`, `right` so that `matrix[i, j] >= (left @ right)[i, j]`
        for all entries.
        """