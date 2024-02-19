from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import List


class AlgoSetting(ABC):
    @property
    @abstractmethod
    def flag_name(self) -> str:
        pass

    @property
    @abstractmethod
    def var_name(self) -> str:
        pass

    @abstractmethod
    def add_arg(self, parser: ArgumentParser):
        pass

    @abstractmethod
    def read_arg(self, args: Namespace):
        pass

    def __init__(self):
        self.was_used_by_algo = False
        self.was_specified_by_user = False

    @staticmethod
    def mark_as_used_by_algo(algo_settings: List["AlgoSetting"]):
        for setting in algo_settings:
            setting.was_used_by_algo = True
