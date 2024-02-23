from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser
from typing import List

from graphblas.core.matrix import Matrix

from src.algo_setting.algo_setting import AlgoSetting
from src.matrix.optimized_matrix import OptimizedMatrix
from src.matrix.format_optimized_matrix import FormatOptimizedMatrix
from src.matrix.lazy_add_optimized_matrix import LazyAddOptimizedMatrix
from src.matrix.matrix_to_optimized_adapter import MatrixToOptimizedAdapter
from src.matrix.short_circuiting_for_empty_matrix import ShortCircuitingForEmptyMatrix


class MatrixOptimizerSetting(AlgoSetting, ABC):
    def __init__(self):
        super().__init__()
        self.is_enabled = True

    @property
    def flag_name(self) -> str:
        return "-disable-" + self.var_name.replace("_", "-")

    def __repr__(self):
        return f"{self.__class__.__name__}(is_enabled={self.is_enabled})"

    def add_arg(self, parser: ArgumentParser):
        parser.add_argument(self.flag_name, dest=self.var_name, default=False, action="store_true")

    def read_arg(self, args: Namespace):
        if args.__getattribute__(self.var_name) is True:
            self.was_specified_by_user = True
            self.is_enabled = False

    def wrap_matrix(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        return self._wrap_matrix_unconditionally(base_matrix) if self.is_enabled else base_matrix

    @abstractmethod
    def _wrap_matrix_unconditionally(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        pass


def optimize_matrix(
    matrix: Matrix,
    settings: List[MatrixOptimizerSetting],
) -> OptimizedMatrix:
    optimized_matrix = MatrixToOptimizedAdapter(matrix)
    for setting in settings:
        optimized_matrix = setting.wrap_matrix(optimized_matrix)
    return optimized_matrix


def get_matrix_optimizer_settings(algo_settings: List[AlgoSetting]) -> List[MatrixOptimizerSetting]:
    return [setting for setting in algo_settings if isinstance(setting, MatrixOptimizerSetting)]


class OptimizeEmptyMatrixSetting(MatrixOptimizerSetting):
    def _wrap_matrix_unconditionally(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        return ShortCircuitingForEmptyMatrix(base_matrix)

    @property
    def var_name(self) -> str:
        return "optimize_empty"


class OptimizeFormatMatrixSetting(MatrixOptimizerSetting):
    def _wrap_matrix_unconditionally(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        return FormatOptimizedMatrix(base_matrix)

    @property
    def var_name(self) -> str:
        return "optimize_format"


class LazyAddMatrixSetting(MatrixOptimizerSetting):
    def _wrap_matrix_unconditionally(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        return LazyAddOptimizedMatrix(base_matrix)

    @property
    def var_name(self) -> str:
        return "lazy_add"
