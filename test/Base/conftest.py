import pytest

from src.problems.Base.algo.matrix_base.format_and_empty_optimized_dynamic_hyper_matrix_base import \
    FormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.format_optimized_dynamic_hyper_matrix_base import \
    FormatOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.iadd_and_format_and_empty_optimized_dynamic_hyper_matrix_base import \
    IAddAndFormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo
from src.problems.Base.algo.matrix_base.simple_dynamic_hyper_matrix_base import SimpleDynamicHyperMatrixBaseAlgo


@pytest.fixture(params=[MatrixBaseAlgo,
                        SimpleDynamicHyperMatrixBaseAlgo,
                        FormatOptimizedDynamicHyperMatrixBaseAlgo,
                        FormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo,
                        IAddAndFormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo
                        ])
def algo(request):
    return request.param
