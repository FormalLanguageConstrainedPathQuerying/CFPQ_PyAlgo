import weakref
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import graphblas
from graphblas.core.dtypes import DataType
from graphblas.core.matrix import Matrix

OPTIMIZE_EMPTY = True

MatrixFormat = Optional[str]

old_ss_init = graphblas.core.ss.matrix.ss.__init__
graphblas.core.ss.matrix.ss.__init__ = lambda self, parent: old_ss_init(self, weakref.proxy(parent))


class EnhancedMatrix(ABC):
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
    def to_matrix(self) -> Matrix:
        pass

    @abstractmethod
    def mxm(self, other: Matrix, swap_operands: bool = False, *args, **kwargs) -> Matrix:
        pass

    def rmxm(self, other: Matrix, *args, **kwargs) -> Matrix:
        return self.mxm(other, swap_operands=True, *args, **kwargs)

    @abstractmethod
    def r_complimentary_mask(self, other: Matrix) -> Matrix:
        pass

    @abstractmethod
    def iadd(self, other: Matrix):
        pass

    @abstractmethod
    def enhance_similarly(self, base: Matrix) -> "EnhancedMatrix":
        pass

    def __iadd__(self, other: Matrix) -> "EnhancedMatrix":
        self.iadd(other)
        return self

    def __str__(self):
        return self.to_matrix().__str__()
