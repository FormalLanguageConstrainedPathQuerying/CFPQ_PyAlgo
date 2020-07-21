from abc import ABC, abstractmethod
from typing import Iterable
from pygraphblas import Matrix
from pygraphblas.types import BOOL

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph


class SingleSourceIndex:
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        self.graph = graph
        self.grammar = grammar
        self.sources = LabelGraph()
        self.nonterms = LabelGraph()

    def init_simple_rules(self):
        for l, r in self.grammar.simple_rules:
            self.nonterms[l] += self.graph[r]


class SingleSourceSolver(ABC):
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        self.graph = graph
        self.grammar = grammar

    @abstractmethod
    def solve(self, sources_vertices: Iterable) -> Matrix:
        pass


class SingleSourceAlgoSmart(SingleSourceSolver):
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        super().__init__(graph, grammar)
        self.index = SingleSourceIndex(graph, grammar)
        self.index.init_simple_rules()

    def solve(self, sources_vertices: Iterable) -> Matrix:
        # Initialize source matrices masks
        for v in sources_vertices:
            self.index.sources[self.index.grammar.start_nonterm][v, v] = True
        # Create temporary matrix
        tmp = Matrix.sparse(BOOL, self.index.graph.matrices_size, self.index.graph.matrices_size)
        # Algo's body
        changed = True
        while changed:
            changed = False
            # Iterate through all complex rules
            for l, r1, r2 in self.index.grammar.complex_rules:

                # Number of instances before operation
                old_nnz = self.index.nonterms[l].nvals

                # l -> r1 r2 ==> l += (l_src * r1) * r2 =>

                # 1) r1_src += {(j, j) : (i, j) \in l_src}
                SingleSourceAlgoSmart.__update_sources(self.index.sources[l], self.index.sources[r1])

                # 2) tmp = l_src * r1
                tmp = self.index.sources[l] @ self.index.nonterms[r1]

                # 3) r2_src += {(j, j) : (i, j) \in tmp}
                SingleSourceAlgoSmart.__update_sources(tmp, self.index.sources[r2])

                # 4) l += tmp * r2
                self.index.nonterms[l] += tmp @ self.index.nonterms[r2]

                # Clear temporary matrix
                tmp.clear()

                # Number of instances after operation
                new_nnz = self.index.nonterms[l].nvals

                # Update changed flag
                changed |= not old_nnz == new_nnz

        return self.index.nonterms[self.index.grammar.start_nonterm]

    @staticmethod
    def __update_sources(src: Matrix, dst: Matrix):
        for j in src.to_lists()[1]:
            dst[j, j] = True


class SingleSourceAlgoBrute(SingleSourceSolver):
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        super().__init__(graph, grammar)

    def solve(self, sources_vertices: Iterable) -> Matrix:
        # Creating new index per solve call
        index = SingleSourceIndex(self.graph, self.grammar)
        # Initialize simple rules
        index.init_simple_rules()
        # Initialize source matrices masks
        for v in sources_vertices:
            index.sources[index.grammar.start_nonterm][v, v] = True
        # Create temporary matrix
        tmp = Matrix.sparse(BOOL, index.graph.matrices_size, index.graph.matrices_size)
        # Algo's body
        changed = True
        while changed:
            changed = False
            # Iterate through all complex rules
            for l, r1, r2 in index.grammar.complex_rules:

                # Number of instances before operation
                old_nnz = index.nonterms[l].nvals

                # l -> r1 r2 ==> l += (l_src * r1) * r2 =>

                # 1) r1_src += {(j, j) : (i, j) \in l_src}
                SingleSourceAlgoBrute.__update_sources(index.sources[l], index.sources[r1])

                # 2) tmp = l_src * r1
                tmp = index.sources[l] @ index.nonterms[r1]

                # 3) r2_src += {(j, j) : (i, j) \in tmp}
                SingleSourceAlgoBrute.__update_sources(tmp, index.sources[r2])

                # 4) l += tmp * r2
                index.nonterms[l] += tmp @ index.nonterms[r2]

                # Clear temporary matrix
                tmp.clear()

                # Number of instances after operation
                new_nnz = index.nonterms[l].nvals

                # Update changed flag
                changed |= not old_nnz == new_nnz

        return index.nonterms[index.grammar.start_nonterm]

    @staticmethod
    def __update_sources(src: Matrix, dst: Matrix):
        for j in src.to_lists()[1]:
            dst[j, j] = True