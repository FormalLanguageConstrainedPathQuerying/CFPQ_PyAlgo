from abc import ABC, abstractmethod
from typing import Tuple

from pygraphblas import Matrix

from src.matrix.enhanced_matrix import EnhancedMatrix, MatrixForm


class AbstractEnhancedMatrixDecorator(EnhancedMatrix, ABC):
    @property
    @abstractmethod
    def base(self) -> EnhancedMatrix:
        pass

    @property
    def nvals(self) -> int:
        return self.base.nvals

    @property
    def shape(self) -> Tuple[int, int]:
        return self.base.shape

    @property
    def format(self) -> MatrixForm:
        return self.base.format

    def to_matrix(self) -> Matrix:
        return self.base.to_matrix()
