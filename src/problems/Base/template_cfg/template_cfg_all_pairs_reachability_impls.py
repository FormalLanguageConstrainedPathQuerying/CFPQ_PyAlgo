from typing import List

from src.problems.Base.template_cfg.matrix.incremental_all_pairs_cfl_reachability_algo import \
    IncrementalAllPairsCFLReachabilityMatrixAlgo
from src.problems.Base.template_cfg.matrix.non_incremental_all_pairs_cfl_reachability_algo import \
    NonIncrementalAllPairsCFLReachabilityMatrixAlgo
from src.problems.Base.template_cfg.template_cfg_all_pairs_reachability import AllPairsCflReachabilityAlgo

ALL_PAIRS_CFL_REACHABILITY_ALGOS: List[AllPairsCflReachabilityAlgo] = [
    IncrementalAllPairsCFLReachabilityMatrixAlgo(),
    NonIncrementalAllPairsCFLReachabilityMatrixAlgo()
]

ALL_PAIRS_CFL_REACHABILITY_ALGO_NAMES = [
    factory.name for factory in ALL_PAIRS_CFL_REACHABILITY_ALGOS
]


def get_all_pairs_cfl_reachability_algo(name: str) -> AllPairsCflReachabilityAlgo:
    for factory in ALL_PAIRS_CFL_REACHABILITY_ALGOS:
        if factory.name == name:
            return factory
    raise ValueError(f"Unknown algorithm name: {name}. "
                     f"Use one of the following names: {ALL_PAIRS_CFL_REACHABILITY_ALGOS}.")
