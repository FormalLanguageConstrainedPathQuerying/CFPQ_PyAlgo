from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, List

from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix

from src.matrix.optimized_matrix import OptimizedMatrix


class HyperVectorOrientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class HyperMatrixSpace(ABC):
    @abstractmethod
    def is_single_cell(self, matrix_shape: Tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def is_hyper_vector(self, matrix_shape: Tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def get_hyper_orientation(self, matrix_shape: Tuple[int, int]) -> HyperVectorOrientation:
        pass

    @abstractmethod
    def reduce_hyper_vector_or_cell(self, hyper_vector_or_cell: Matrix) -> Matrix:
        pass

    @abstractmethod
    def hyper_rotate(self, hyper_vector: Matrix, orientation: HyperVectorOrientation) -> Matrix:
        pass

    @abstractmethod
    def to_block_diag_matrix(self, hyper_vector: Matrix) -> Matrix:
        pass

    @abstractmethod
    def create_hyper_vector(self, typ: DataType, orientation: HyperVectorOrientation) -> Matrix:
        pass

    @abstractmethod
    def create_hyper_cell(self, typ: DataType) -> Matrix:
        pass

    def create_space_element(self, typ: DataType, is_vector: bool) -> Matrix:
        return (
            self.create_hyper_vector(typ, HyperVectorOrientation.VERTICAL)
            if is_vector
            else self.create_hyper_cell(typ)
        )

    @abstractmethod
    def stack_into_hyper_column(self, matrices: List[Matrix]) -> Matrix:
        pass

    @abstractmethod
    def repeat_into_hyper_column(self, matrix: Matrix) -> Matrix:
        pass

    @abstractmethod
    def wrap_enhanced_hyper_matrix(self, base: "OptimizedMatrix") -> OptimizedMatrix:
        pass
