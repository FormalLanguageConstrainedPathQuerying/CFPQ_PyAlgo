from src.matrix.enhanced_matrix import EnhancedMatrix
from src.problems.Base.algo.matrix_base.abstract_dynamic_hyper_matrix_base import AbstractDynamicHyperMatrixBaseAlgo


class SimpleDynamicHyperMatrixBaseAlgo(AbstractDynamicHyperMatrixBaseAlgo):
    def non_hyper_enhance_matrix(self, base_matrix: EnhancedMatrix, var_name: str) -> EnhancedMatrix:
        return base_matrix
