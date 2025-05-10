from cfpq_decomposer.decomposer import Decomposer
from cfpq_decomposer.high_performance_decomposer import HighPerformanceDecomposer
from test.cfpq_decomposer.test_abstract_decomposer import AbstractDecomposerTest

class TestHighPerformanceDecomposer(AbstractDecomposerTest):
    def create_decomposer(self) -> Decomposer:
        return HighPerformanceDecomposer()
