from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, List

from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix
from graphblas.core.operator import Monoid

from cfpq_matrix.optimized_matrix import OptimizedMatrix


class BlockMatrixOrientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class BlockMatrixSpace(ABC):
    """
    This class provides methods for manipulating `BlockMatrixSpace` elements.

    There are two types of `BlockMatrixSpace` elements:
      - cell (regular matrix)
      - hyper vector (a bunch of regular matrices (blocks) stacked next to each other)

    Within one `BlockMatrixSpace`:
      - all cells have the same shape `(n, n)`
      - each hyper vector either has shape `(self.block_count * n, n)` or `(n, self.block_count * n)`

    If you are using `OptimizedMatrix` class, then you can just wrap all your
     `OptimizedMatrix` class instances by calling `automize_block_operations()` method
     and all the managing of block matrices will automatically be performed for you as follows:
       - Any operation on two cells is directly performed on the underlying matrices
       - Any operation on two hyper vectors is performed block-wise
       - When cell and hyper vector are multiplied, then a cell is multiplied by each block of a hyper vector
       - When hyper vector is added in-place to a cell, then sum of hyper vector's blocks is added to a cell
       - When cell is added in-place to a hyper vector, then cell is added to each of hyper vector's blocks
       - Subtracting cells from hyper-vectors and vice-versa is not supported
       - Rotated copies of your matrix may be cached to improve performance
    """

    @property
    @abstractmethod
    def block_count(self) -> int:
        pass

    @abstractmethod
    def automize_block_operations(self, base: "OptimizedMatrix") -> OptimizedMatrix:
        pass

    @abstractmethod
    def is_single_cell(self, matrix_shape: Tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def is_hyper_vector(self, matrix_shape: Tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def get_block_matrix_orientation(self, matrix_shape: Tuple[int, int]) -> BlockMatrixOrientation:
        pass

    @abstractmethod
    def reduce_hyper_vector_or_cell(self, hyper_vector_or_cell: Matrix, op: Monoid) -> Matrix:
        """
        If `hyper_vector_or_cell` is a hyper vector, then sum of its blocks is returned.
        If `hyper_vector_or_cell` is a cell, then underlying matrix is return.
        """
        pass

    @abstractmethod
    def hyper_rotate(self, hyper_vector: Matrix, orientation: BlockMatrixOrientation) -> Matrix:
        pass

    @abstractmethod
    def to_block_diag_matrix(self, hyper_vector: Matrix) -> Matrix:
        pass

    @abstractmethod
    def create_hyper_vector(self, typ: DataType, orientation: BlockMatrixOrientation) -> Matrix:
        pass

    @abstractmethod
    def create_cell(self, typ: DataType) -> Matrix:
        pass

    def create_space_element(self, typ: DataType, is_vector: bool) -> Matrix:
        return (
            self.create_hyper_vector(typ, BlockMatrixOrientation.VERTICAL)
            if is_vector
            else self.create_cell(typ)
        )

    @abstractmethod
    def stack_into_hyper_column(self, matrices: List[Matrix]) -> Matrix:
        pass

    @abstractmethod
    def repeat_into_hyper_column(self, matrix: Matrix) -> Matrix:
        pass

    @abstractmethod
    def get_hyper_vector_blocks(self, hyper_vector: Matrix) -> List[Matrix]:
        pass
