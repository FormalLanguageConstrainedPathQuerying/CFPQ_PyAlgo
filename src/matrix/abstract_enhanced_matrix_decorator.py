from abc import ABC, abstractmethod
from typing import Tuple

from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix

from src.matrix.enhanced_matrix import EnhancedMatrix, MatrixForm

# EnhancedMatrix
# - MatrixToEnhancedAdapter
# - AbstractEnhancedMatrixDecorator
# - IAddOptimizedMatrix
# - FormatOptimizedMatrix
# - HyperMatrix


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

    @property
    def dtype(self) -> DataType:
        return self.base.dtype

    def to_matrix(self) -> Matrix:
        return self.base.to_matrix()
