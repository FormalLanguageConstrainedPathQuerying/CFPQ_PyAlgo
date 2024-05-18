from abc import ABC, abstractmethod
from typing import Optional, Tuple

from pygraphblas import Matrix
from pygraphblas.binaryop import BinaryOp
from pygraphblas.semiring import Semiring
from pygraphblas.types import Type

from cfpq_matrix.subtractable_semiring import SubOp

# see pygraphblas.lib.GxB_BY_ROW and pygraphblas.lib.GxB_BY_COL
MatrixFormat = Optional[int]


class OptimizedMatrix(ABC):
    """
    Interface including core matrix operations,
    that many performance-oriented decorators implement.
    """
    @property
    @abstractmethod
    def nvals(self) -> int:
        pass

    @property
    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        pass

    @property
    @abstractmethod
    def format(self) -> MatrixFormat:
        pass

    @property
    @abstractmethod
    def dtype(self) -> Type:
        pass

    @abstractmethod
    def to_unoptimized(self) -> Matrix:
        pass

    @abstractmethod
    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        pass

    @abstractmethod
    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        """
        Returns the result of subtracting `self` from `other`.
        """

    @abstractmethod
    def iadd(self, other: Matrix, op: BinaryOp):
        """
        Adds `other` to `self` in-place.
        """

    @abstractmethod
    def optimize_similarly(self, other: Matrix) -> "OptimizedMatrix":
        """
        Applies to `other` matrix all optimizations that are applied to `self` matrix.
        """

    def __str__(self):
        return self.to_unoptimized().__str__()
