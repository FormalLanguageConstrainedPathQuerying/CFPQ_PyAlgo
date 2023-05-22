from typing import Final

from src.problems.Base.algo.matrix_base.matrix_base import MatrixBaseAlgo

from src.problems.AllPaths.algo.tensor.tensor import TensorSimpleAlgo
from src.problems.AllPaths.algo.tensor.tensor import TensorDynamicAlgo
from src.problems.Base.algo.tensor.one_terminal_tensor import OneTerminalTensorAlgo, OneTerminalDynamicTensorAlgo

from src.problems.SinglePath.algo.matrix_single_path.matrix_single_path_index import MatrixSingleAlgo

from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSOptAlgo
from src.problems.MultipleSource.algo.matrix_ms.matrix_ms import MatrixMSBruteAlgo
from benchmark.mutate_graph import process_multiedge_ma, process_multiedge_java

"""
Correspondence of algo and problem it solves
"""
ALGO_PROBLEM: Final = {'TensorSimple': 'AllPaths',
                       'TensorDynamic': 'AllPaths',
                       'MatrixBase': 'Base',
                       'MatrixMSBrute': 'MS',
                       'MatrixMSOpt': 'MS',
                       'MatrixSingle': 'SinglePath',
                       'OneTerminalTensorMA': 'OneTerminalReachability',
                       'OneTerminalDynamicTensorMA': 'OneTerminalReachability',
                       'OneTerminalTensorJava': 'OneTerminalReachability',
                       'OneTerminalDynamicTensorJava': 'OneTerminalReachability',
                       }

"""
Matching name of algo and its implementation
"""
ALGO_IMPL: Final = {'TensorSimple': TensorSimpleAlgo,
                    'TensorDynamic': TensorDynamicAlgo,
                    'MatrixBase': MatrixBaseAlgo,
                    'MatrixMSBrute': MatrixMSBruteAlgo,
                    'MatrixMSOpt': MatrixMSOptAlgo,
                    'MatrixSingle': MatrixSingleAlgo,
                    'OneTerminalTensorMA': (OneTerminalTensorAlgo, process_multiedge_ma),
                    'OneTerminalDynamicTensorMA': (OneTerminalDynamicTensorAlgo, process_multiedge_ma),
                    'OneTerminalTensorJava': (OneTerminalTensorAlgo, process_multiedge_java),
                    'OneTerminalDynamicTensorJava': (OneTerminalDynamicTensorAlgo, process_multiedge_java),
                    }
