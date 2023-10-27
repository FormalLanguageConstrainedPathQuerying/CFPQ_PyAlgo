import pytest

from src.problems.Base.algo.matrix_base.format_optimized_dynamic_hyper_matrix_base import \
    FormatOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.iadd_and_format_optimized_dynamic_hyper_matrix_base import \
    IAddAndFormatOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo
from src.problems.Base.algo.matrix_base.simple_dynamic_hyper_matrix_base import SimpleDynamicHyperMatrixBaseAlgo


@pytest.fixture(params=[MatrixBaseAlgo,
                        SimpleDynamicHyperMatrixBaseAlgo,
                        FormatOptimizedDynamicHyperMatrixBaseAlgo,
                        IAddAndFormatOptimizedDynamicHyperMatrixBaseAlgo
                        ])
def algo(request):
    return request.param
