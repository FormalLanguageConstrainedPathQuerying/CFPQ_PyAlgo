from abc import ABC, abstractmethod
from typing import Tuple

from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix

from src.matrix.optimized_matrix import OptimizedMatrix, MatrixFormat


class AbstractOptimizedMatrixDecorator(OptimizedMatrix, ABC):
    @property
    @abstractmethod
    def base(self) -> OptimizedMatrix:
        pass

    @property
    def nvals(self) -> int:
        return self.base.nvals

    @property
    def shape(self) -> Tuple[int, int]:
        return self.base.shape

    @property
    def format(self) -> MatrixFormat:
        return self.base.format

    @property
    def dtype(self) -> DataType:
        return self.base.dtype

    def to_unoptimized(self) -> Matrix:
        return self.base.to_unoptimized()
