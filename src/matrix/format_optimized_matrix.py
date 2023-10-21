import warnings

from graphblas.core.matrix import Matrix

from src.matrix.abstract_enhanced_matrix_decorator import AbstractEnhancedMatrixDecorator
from src.matrix.enhanced_matrix import EnhancedMatrix
from src.utils.unique_ptr import unique_ptr


class FormatOptimizedMatrix(AbstractEnhancedMatrixDecorator):
    def __new__(
            cls,
            base: EnhancedMatrix,
            discard_base_on_reformat: bool = False,
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
    def base(self) -> EnhancedMatrix:
        return self._base

    def _force_init_format(self, desired_format: str) -> EnhancedMatrix:
        # if desired_format == self.base.format:
        #     self.discard_base_on_reformat = False
        if desired_format not in self.matrices:
            # print("force reformat", desired_format)
            base_matrix = unique_ptr(self.base.to_matrix().dup())
            base_matrix.ss.config["format"] = desired_format
            self.matrices[desired_format] = self.base.enhance_similarly(base_matrix)
            if self.discard_base_on_reformat:
                del self.matrices[self.base.format]
                self._base = self.matrices[desired_format]
                self.discard_base_on_reformat = False
        res = self.matrices[desired_format]
        return res

    # def _with_format_if_needed(self, other: Matrix, desired_format: MatrixFormat) -> "EnhancedMatrix":
    #     if ((self.format == MatrixFormat.BOTH and other.nvals < self.nvals) or
    #             other.nvals < self.nvals / self.size_diff_reformat_threshold):
    #         other.format = desired_format.to_graphblas_format()
    #         return self.base.with_format(desired_format)
    #     return self.base

    def mxm(self, other: Matrix, swap_operands: bool = False, *args, **kwargs) -> Matrix:
        left_nvals = other.nvals if swap_operands else self.nvals
        right_nvals = self.nvals if swap_operands else other.nvals
        desired_format = "by_row" if left_nvals < right_nvals else "by_col"

        # if desired_format not in self.matrices:
        #     print("self.nvals:", self.nvals, "other.nvals:", other.nvals)
        if desired_format in self.matrices or other.nvals < self.nvals / self.reformat_threshold:
            other.ss.config["format"] = desired_format
            reformatted_self = self._force_init_format(desired_format)
            return reformatted_self.mxm(other, swap_operands=swap_operands, *args, **kwargs)
        return self.base.mxm(other, swap_operands=swap_operands, *args, **kwargs)

    def r_complimentary_mask(self, other: Matrix) -> Matrix:
        return self.matrices.get(other.ss.config["format"], self.base).r_complimentary_mask(other)

    def iadd(self, other: Matrix):
        for m in self.matrices.values():
            m.iadd(other)

    def enhance_similarly(self, base: Matrix) -> EnhancedMatrix:
        return FormatOptimizedMatrix(self.base.enhance_similarly(base), reformat_threshold=self.reformat_threshold)

    def __sizeof__(self):
        return sum(m.__sizeof__() for m in self.matrices.values())
