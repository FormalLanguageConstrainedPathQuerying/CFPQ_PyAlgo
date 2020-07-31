from abc import ABC, abstractmethod
from typing import Iterable
from pygraphblas import Matrix
from pygraphblas.types import BOOL

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph


def update_sources(src: Matrix, dst: Matrix):
    """ dst += {(j, j) : (i, j) \in src} by GrB_reduce src to a vector """

    # Transpose src and reduce to a vector
    J, V = src.T.reduce_vector().to_lists()

    # If j-th column of src contains True then add (j, j) to dst
    for k in range(len(J)):
        if V[k] is True:
            dst[J[k], J[k]] = True


class SingleSourceIndex:
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        self.graph = graph
        self.grammar = grammar
        self.sources = LabelGraph(graph.matrices_size)
        self.nonterms = LabelGraph(graph.matrices_size)

    def init_simple_rules(self):
        for l, r in self.grammar.simple_rules:
            self.nonterms[l] += self.graph.matrices[r]


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

            # Number of instances before operation
            old_nnz_nonterms = {nonterm: self.index.nonterms[nonterm].nvals for nonterm in self.index.nonterms}
            old_nnz_src = {nonterm: self.index.sources[nonterm].nvals for nonterm in self.index.sources}

            # Iterate through all complex rules
            for l, r1, r2 in self.index.grammar.complex_rules:
                # l -> r1 r2 ==> l += (l_src * r1) * r2 =>

                # 1) r1_src += {(j, j) : (i, j) \in l_src}
                update_sources(self.index.sources[l], self.index.sources[r1])

                # 2) tmp = l_src * r1
                tmp = self.index.sources[l] @ self.index.nonterms[r1]

                # 3) r2_src += {(j, j) : (i, j) \in tmp}
                update_sources(tmp, self.index.sources[r2])

                # 4) l += tmp * r2
                self.index.nonterms[l] += tmp @ self.index.nonterms[r2]

            # Number of instances after operation
            new_nnz_nonterms = {nonterm: self.index.nonterms[nonterm].nvals for nonterm in self.index.nonterms}
            new_nnz_src = {nonterm: self.index.sources[nonterm].nvals for nonterm in self.index.sources}

            # Update changed flag
            changed |= (not (old_nnz_nonterms == new_nnz_nonterms)) or (not (old_nnz_src == new_nnz_src))

        return self.index.nonterms[self.index.grammar.start_nonterm]


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

            # Number of instances before operation
            old_nnz_nonterms = {nonterm: index.nonterms[nonterm].nvals for nonterm in index.nonterms}
            old_nnz_src = {nonterm: index.sources[nonterm].nvals for nonterm in index.sources}

            # Iterate through all complex rules
            for l, r1, r2 in index.grammar.complex_rules:
                # l -> r1 r2 ==> l += (l_src * r1) * r2 =>

                # 1) r1_src += {(j, j) : (i, j) \in l_src}
                update_sources(index.sources[l], index.sources[r1])

                # 2) tmp = l_src * r1
                tmp = index.sources[l] @ index.nonterms[r1]

                # 3) r2_src += {(j, j) : (i, j) \in tmp}
                update_sources(tmp, index.sources[r2])

                # 4) l += tmp * r2
                index.nonterms[l] += tmp @ index.nonterms[r2]

            # Number of instances after operation
            new_nnz_nonterms = {nonterm: index.nonterms[nonterm].nvals for nonterm in index.nonterms}
            new_nnz_src = {nonterm: index.sources[nonterm].nvals for nonterm in index.sources}

            changed |= (not (old_nnz_nonterms == new_nnz_nonterms)) or (not (old_nnz_src == new_nnz_src))

        return index.nonterms[index.grammar.start_nonterm]
