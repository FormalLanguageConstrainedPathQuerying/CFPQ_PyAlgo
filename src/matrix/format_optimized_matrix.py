import warnings

from graphblas.core.matrix import Matrix
from graphblas.core.operator import Monoid, Semiring

from src.matrix.abstract_optimized_matrix_decorator import AbstractOptimizedMatrixDecorator
from src.matrix.optimized_matrix import OptimizedMatrix
from src.utils.subtractable_semiring import SubOp


class FormatOptimizedMatrix(AbstractOptimizedMatrixDecorator):
    def __new__(
            cls,
            base: OptimizedMatrix,
            discard_base_on_reformat: bool = True,
            reformat_threshold: int = 3.0
    ):
        if base.format is None:
            warnings.warn("EnhancedMatrix format is attempted to be optimized twice, "
                          f"ignoring outer reformat_threshold: {reformat_threshold}.")
            return base
        self = object.__new__(cls)
        self.reformat_threshold = reformat_threshold
        self.discard_base_on_reformat = discard_base_on_reformat
        self._base = base
        self.matrices = {base.format: base}
        return self

    @property
    def base(self) -> OptimizedMatrix:
        return self._base

    def _force_init_format(self, desired_format: str) -> OptimizedMatrix:
        # if desired_format == self.base.format:
        #     self.discard_base_on_reformat = False
        if desired_format not in self.matrices:
            # print("force reformat", desired_format)
            base_matrix = self.base.to_unoptimized().dup()
            base_matrix.ss.config["format"] = desired_format
            self.matrices[desired_format] = self.base.optimize_similarly(base_matrix)
            if self.discard_base_on_reformat:
                del self.matrices[self.base.format]
                self._base = self.matrices[desired_format]
        self.discard_base_on_reformat = False
        res = self.matrices[desired_format]
        return res

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        left_nvals = other.nvals if swap_operands else self.nvals
        right_nvals = self.nvals if swap_operands else other.nvals
        desired_format = "by_row" if left_nvals < right_nvals else "by_col"

        # if desired_format not in self.matrices:
        #     print("self.nvals:", self.nvals, "other.nvals:", other.nvals)
        if desired_format in self.matrices or other.nvals < self.nvals / self.reformat_threshold:
            other.ss.config["format"] = desired_format
            reformatted_self = self._force_init_format(desired_format)
            return reformatted_self.mxm(other, op, swap_operands=swap_operands)
        return self.base.mxm(other, op, swap_operands=swap_operands)

    def rsub(self, other: Matrix, op: SubOp) -> Matrix:
        return self.matrices.get(other.ss.config["format"], self.base).rsub(other, op)

    def iadd(self, other: Matrix, op: Monoid):
        for m in self.matrices.values():
            m.iadd(other, op)

    def optimize_similarly(self, other: Matrix) -> OptimizedMatrix:
        return FormatOptimizedMatrix(self.base.optimize_similarly(other), reformat_threshold=self.reformat_threshold)

    def __sizeof__(self):
        return sum(m.__sizeof__() for m in self.matrices.values())
