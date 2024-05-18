from dataclasses import dataclass
from typing import Callable, Any

from pygraphblas import Matrix
from pygraphblas.semiring import Semiring

SubOp = Callable[[Matrix, Matrix], Matrix]


@dataclass
class SubtractableSemiring:
    one: Any
    semiring: Semiring
    sub_op: SubOp
