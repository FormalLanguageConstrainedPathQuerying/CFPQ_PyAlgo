from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, List

from pygraphblas import Matrix

from src.matrix.enhanced_matrix import EnhancedMatrix

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

    def create_hyper_vector(self, typ, orientation: HyperVectorOrientation) -> Matrix:
        pass

    @abstractmethod
    def stack_into_hyper_column(self, matrices: List[Matrix]) -> Matrix:
        pass

    @abstractmethod
    def wrap_enhanced_hyper_matrix(self, base: "EnhancedMatrix") -> "EnhancedMatrix":
        pass
