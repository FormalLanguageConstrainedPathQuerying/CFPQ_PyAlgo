import weakref
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import graphblas
from graphblas import Matrix
from graphblas.core.dtypes import DataType
from graphblas.core.operator import Semiring, Monoid

from src.utils.subtractable_semiring import SubOp

OPTIMIZE_EMPTY = True

MatrixFormat = Optional[str]

old_ss_init = graphblas.core.ss.matrix.ss.__init__
graphblas.core.ss.matrix.ss.__init__ = lambda self, parent: old_ss_init(self, weakref.proxy(parent))


class OptimizedMatrix(ABC):
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
        pass

    @abstractmethod
    def iadd(self, other: Matrix, op: Monoid):
        pass

    @abstractmethod
    def optimize_similarly(self, other: Matrix) -> "OptimizedMatrix":
        pass

    def __str__(self):
        return self.to_unoptimized().__str__()
