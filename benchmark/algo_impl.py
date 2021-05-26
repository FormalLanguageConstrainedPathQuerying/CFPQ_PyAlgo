from typing import Final

from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo

from src.problems.AllPaths.algo.tensor.tensor import TensorSimpleAlgo
from src.problems.AllPaths.algo.tensor.tensor import TensorDynamicAlgo

from src.problems.SinglePath.algo.matrix_single_path.matrix_single_path_index import MatrixSingleAlgo

from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSOptAlgo
from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSSmartAlgo
from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSBruteAlgo

"""
Correspondence of algo and problem it solves
"""
ALGO_PROBLEM: Final = {'TensorSimple': 'AllPath',
                       'TensorDynamic': 'AllPath',
                       'MatrixBase': 'Base',
                       'MatrixMSBrute': 'MS',
                       'MatrixMSSmart': 'MS',
                       'MatrixMSOpt': 'MS',
                       'MatrixSingle': 'SinglePath'}

"""
Matching name of algo and its implementation
"""
ALGO_IMPL: Final = {'TensorSimple': TensorSimpleAlgo,
                    'TensorDynamic': TensorDynamicAlgo,
                    'MatrixBase': MatrixBaseAlgo,
                    'MatrixMSBrute': MatrixMSBruteAlgo,
                    'MatrixMSSmart': MatrixMSSmartAlgo,
                    'MatrixMSOpt': MatrixMSOptAlgo,
                    'MatrixSingle': MatrixSingleAlgo}
