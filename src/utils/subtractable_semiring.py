from dataclasses import dataclass
from typing import Callable, Any

from graphblas.core.matrix import Matrix
from graphblas.core.operator import Semiring

SubOp = Callable[[Matrix, Matrix], Matrix]


@dataclass
class SubtractableSemiring:
    one: Any
    semiring: Semiring
    sub_op: SubOp
