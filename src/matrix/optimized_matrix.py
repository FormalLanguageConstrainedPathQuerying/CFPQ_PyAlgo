import weakref
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import graphblas
from graphblas import Matrix
from graphblas.core.dtypes import DataType
from graphblas.core.operator import Semiring, Monoid

from src.utils.subtractable_semiring import SubOp

MatrixFormat = Optional[str]

# This is a hack that prevents `graphblas` from creating strong reference cycles
# This hack makes reference-counting garbage collection possible
old_ss_init = graphblas.core.ss.matrix.ss.__init__
graphblas.core.ss.matrix.ss.__init__ = lambda self, parent: old_ss_init(self, weakref.proxy(parent))


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
    def dtype(self) -> DataType:
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
        pass

    @abstractmethod
    def iadd(self, other: Matrix, op: Monoid):
        """
        Adds `other` to `self` in-place.
        """
        pass

    @abstractmethod
    def optimize_similarly(self, other: Matrix) -> "OptimizedMatrix":
        """
        Applies to `other` matrix all optimizations that are applied to `self` matrix.
        """
        pass

    def __str__(self):
        return self.to_unoptimized().__str__()
