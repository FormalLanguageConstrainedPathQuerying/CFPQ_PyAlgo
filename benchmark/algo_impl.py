from typing import Final

from src.problems.Base.algo.matrix_base.format_and_empty_optimized_dynamic_hyper_matrix_base import \
    FormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.format_optimized_dynamic_hyper_matrix_base import \
    FormatOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.hyper_matrix_base import HyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.iadd_and_format_and_empty_optimized_dynamic_hyper_matrix_base import \
    IAddAndFormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo
from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo

from src.problems.AllPaths.algo.tensor.tensor import TensorSimpleAlgo
from src.problems.AllPaths.algo.tensor.tensor import TensorDynamicAlgo
from src.problems.Base.algo.matrix_base.simple_dynamic_hyper_matrix_base import SimpleDynamicHyperMatrixBaseAlgo

from src.problems.SinglePath.algo.matrix_single_path.matrix_single_path_index import MatrixSingleAlgo

from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSOptAlgo
from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSBruteAlgo

"""
Correspondence of algo and problem it solves
"""
ALGO_PROBLEM: Final = {'TensorSimple': 'AllPaths',
                       'TensorDynamic': 'AllPaths',
                       'MatrixBase': 'Base',
                       'HyperMatrixBase': 'Base',
                       'SimpleDynamicHyperMatrixBase': 'Base',
                       'FormatOptimizedDynamicHyperMatrixBase': 'Base',
                       'IAddAndFormatOptimizedDynamicHyperMatrixBase': 'Base',
                       'MatrixMSBrute': 'MS',
                       'MatrixMSOpt': 'MS',
                       'MatrixSingle': 'SinglePath'}

"""
Matching name of algo and its implementation
"""
ALGO_IMPL: Final = {'TensorSimple': TensorSimpleAlgo,
                    'TensorDynamic': TensorDynamicAlgo,
                    'MatrixBase': MatrixBaseAlgo,
                    'HyperMatrixBase': HyperMatrixBaseAlgo,
                    'SimpleDynamicHyperMatrixBase': SimpleDynamicHyperMatrixBaseAlgo,
                    'FormatOptimizedDynamicHyperMatrixBase': FormatOptimizedDynamicHyperMatrixBaseAlgo,
                    'FormatAndEmptyOptimizedDynamicHyperMatrixBase': FormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo,
                    'IAddAndFormatAndEmptyOptimizedDynamicHyperMatrixBase':
                        IAddAndFormatAndEmptyOptimizedDynamicHyperMatrixBaseAlgo,
                    'MatrixMSBrute': MatrixMSBruteAlgo,
                    'MatrixMSOpt': MatrixMSOptAlgo,
                    'MatrixSingle': MatrixSingleAlgo}
