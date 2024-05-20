from itertools import product

import pytest

from cfpq_algo.setting.algo_settings_manager import AlgoSettingsManager
from cfpq_algo.all_pairs.all_cfl_pairs_reachability_impls import \
    ALL_PAIRS_CFL_REACHABILITY_ALGO_NAMES


@pytest.fixture(params=ALL_PAIRS_CFL_REACHABILITY_ALGO_NAMES)
def algo_name(request):
    return request.param


def pytest_generate_tests(metafunc):
    if "algo_settings" in metafunc.fixturenames:
        bool_combinations = list(product([True, False], repeat=len(AlgoSettingsManager.create_settings())))
        setting_combinations = []

        for bool_combination in bool_combinations:
            settings = AlgoSettingsManager.create_settings()
            for setting, is_enabled in zip(settings, bool_combination):
                setting.is_enabled = is_enabled
            setting_combinations.append(settings)

        metafunc.parametrize(
            "algo_settings",
            setting_combinations,
            ids=[str(setting) for setting in setting_combinations]
        )
