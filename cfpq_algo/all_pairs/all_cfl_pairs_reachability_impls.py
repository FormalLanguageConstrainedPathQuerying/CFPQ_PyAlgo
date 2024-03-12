from typing import List

from cfpq_algo.all_pairs.matrix.incremental_all_pairs_cfl_reachability_algo import \
    IncrementalAllPairsCFLReachabilityMatrixAlgo
from cfpq_algo.all_pairs.matrix.non_incremental_all_pairs_cfl_reachability_algo import \
    NonIncrementalAllPairsCFLReachabilityMatrixAlgo
from cfpq_algo.all_pairs.all_pairs_cfl_reachability_algo import AllPairsCflReachabilityAlgo

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
