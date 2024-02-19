import warnings
from argparse import ArgumentParser, Namespace
from typing import List

from src.algo_setting.algo_setting import AlgoSetting
from src.matrix.matrix_optimizer_setting import OptimizeEmptyMatrixSetting, LazyAddMatrixSetting, \
    OptimizeFormatMatrixSetting


class AlgoSettingsManager:
    def __init__(self):
        self._settings: List[AlgoSetting] = self.create_settings()

    @staticmethod
    def create_settings():
        # NOTE: changing order of settings may change the semantics
        return [
            OptimizeEmptyMatrixSetting(),
            LazyAddMatrixSetting(),
            OptimizeFormatMatrixSetting()
        ]

    def add_args(self, parser: ArgumentParser):
        for setting in self._settings:
            setting.add_arg(parser)

    def read_args(self, args: Namespace) -> List[AlgoSetting]:
        for setting in self._settings:
            setting.read_arg(args)
        return self._settings

    def report_unused(self):
        for setting in self._settings:
            if setting.was_specified_by_user and not setting.was_used_by_algo:
                warnings.warn(f"Algo setting '{setting.flag_name}' was specified, but was not used by the algorithm.")
