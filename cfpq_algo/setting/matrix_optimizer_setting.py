from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser
from typing import List, Callable

from graphblas.core.matrix import Matrix

from cfpq_algo.setting.algo_setting import AlgoSetting
from cfpq_matrix.optimized_matrix import OptimizedMatrix
from cfpq_matrix.format_optimized_matrix import FormatOptimizedMatrix
from cfpq_matrix.lazy_add_optimized_matrix import LazyAddOptimizedMatrix
from cfpq_matrix.matrix_to_optimized_adapter import MatrixToOptimizedAdapter
from cfpq_matrix.empty_optimized_matrix import EmptyOptimizedMatrix


def create_matrix_optimizer(algo_settings: List[AlgoSetting]) -> Callable[[Matrix], OptimizedMatrix]:
    optimizer_settings = get_matrix_optimizer_settings(algo_settings)
    return lambda matrix: optimize_matrix(matrix, optimizer_settings)


class MatrixOptimizerSetting(AlgoSetting, ABC):
    def __init__(self):
        super().__init__()
        self.is_enabled = True

    @property
    def flag_name(self) -> str:
        return "--disable-" + self.var_name.replace("_", "-")

    @property
    @abstractmethod
    def help(self) -> str:
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(is_enabled={self.is_enabled})"

    def add_arg(self, parser: ArgumentParser):
        parser.add_argument(
            self.flag_name,
            dest=self.var_name,
            default=False,
            action="store_true",
            help=self.help
        )

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
    AlgoSetting.mark_as_used_by_algo(settings)
    for setting in settings:
        optimized_matrix = setting.wrap_matrix(optimized_matrix)
    return optimized_matrix


def get_matrix_optimizer_settings(algo_settings: List[AlgoSetting]) -> List[MatrixOptimizerSetting]:
    return [setting for setting in algo_settings if isinstance(setting, MatrixOptimizerSetting)]


class OptimizeEmptyMatrixSetting(MatrixOptimizerSetting):
    def _wrap_matrix_unconditionally(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        return EmptyOptimizedMatrix(base_matrix)

    @property
    def var_name(self) -> str:
        return "optimize_empty"

    @property
    def help(self) -> str:
        return "Turns off empty matrix optimization."


class OptimizeFormatMatrixSetting(MatrixOptimizerSetting):
    def _wrap_matrix_unconditionally(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        return FormatOptimizedMatrix(base_matrix)

    @property
    def var_name(self) -> str:
        return "optimize_format"

    @property
    def help(self) -> str:
        return "Turns off matrix format optimization."


class LazyAddMatrixSetting(MatrixOptimizerSetting):
    def _wrap_matrix_unconditionally(self, base_matrix: OptimizedMatrix) -> OptimizedMatrix:
        return LazyAddOptimizedMatrix(base_matrix)

    @property
    def var_name(self) -> str:
        return "lazy_add"

    @property
    def help(self) -> str:
        return "Turns off lazy addition optimization."
