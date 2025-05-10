from cfpq_decomposer.decomposer import Decomposer
from cfpq_decomposer.prototype_decomposer import PrototypeDecomposer
from test.cfpq_decomposer.test_abstract_decomposer import AbstractDecomposerTest


class TestPrototypeDecomposer(AbstractDecomposerTest):
    def create_decomposer(self) -> Decomposer:
        return PrototypeDecomposer()
