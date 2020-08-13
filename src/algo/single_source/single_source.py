from abc import ABC, abstractmethod
from typing import Iterable, Tuple
from pygraphblas import Matrix, TransposeA
from pygraphblas.types import BOOL

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph


def update_sources(m: Matrix, dst: Matrix):
    """ dst += {(j, j) : (i, j) in m} by GrB_reduce src to a vector """

    # Transpose src and reduce to a vector
    J, V = m.T.reduce_vector().to_lists()

    # If j-th column of src contains True then add (j, j) to dst
    for k in range(len(J)):
        if V[k] is True:
            dst[J[k], J[k]] = True


def update_sources_opt(m: Matrix, mask: Matrix, res: Matrix):
    """ res += {(j, j): (i, j) in m and (j, j) not in mask}"""
    src_vec = m.reduce_vector(desc=TransposeA)
    for i, _ in src_vec:
        if (i, i) not in mask:
            res[i, i] = 1


class SingleSourceIndex:
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        self.graph = graph
        self.grammar = grammar
        self.sources = LabelGraph(graph.matrices_size)
        self.nonterms = LabelGraph(graph.matrices_size)

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

            # Number of instances before operation
            old_nnz_nonterms = {nonterm: self.index.nonterms[nonterm].nvals for nonterm in self.index.grammar.nonterms}
            old_nnz_sources = {nonterm: self.index.sources[nonterm].nvals for nonterm in self.index.grammar.nonterms}

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
            new_nnz_nonterms = {nonterm: self.index.nonterms[nonterm].nvals for nonterm in self.index.grammar.nonterms}
            new_nnz_sources = {nonterm: self.index.sources[nonterm].nvals for nonterm in self.index.grammar.nonterms}

            # Update changed flag
            changed |= (not (old_nnz_nonterms == new_nnz_nonterms)) or (not (old_nnz_sources == new_nnz_sources))

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
            old_nnz_nonterms = {nonterm: index.nonterms[nonterm].nvals for nonterm in index.grammar.nonterms}
            old_nnz_sources = {nonterm: index.sources[nonterm].nvals for nonterm in index.grammar.nonterms}

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
            new_nnz_nonterms = {nonterm: index.nonterms[nonterm].nvals for nonterm in index.grammar.nonterms}
            new_nnz_sources = {nonterm: index.sources[nonterm].nvals for nonterm in index.grammar.nonterms}

            # Update changed flag
            changed |= (not (old_nnz_nonterms == new_nnz_nonterms)) or (not (old_nnz_sources == new_nnz_sources))

        return index.nonterms[index.grammar.start_nonterm]


class SingleSourceAlgoOpt(SingleSourceSolver):
    def __init__(self, graph: LabelGraph, grammar: CnfGrammar):
        super().__init__(graph, grammar)
        self.index = SingleSourceIndex(graph, grammar)
        self.index.init_simple_rules()

    def solve(self, sources_vertices: Iterable) -> Matrix:
        new_sources = LabelGraph(self.graph.matrices_size)

        # Initialize source matrices masks
        for i in sources_vertices:
            if (i, i) not in self.index.sources[self.grammar.start_nonterm]:
                new_sources[self.grammar.start_nonterm][i, i] = True

        # Create temporary matrix
        tmp = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)

        # Algo's body
        changed = True
        while changed:
            changed = False

            # Number of instances before operation
            old_nnz_nonterms = {nonterm: self.index.nonterms[nonterm].nvals for nonterm in self.grammar.nonterms}
            old_nnz_sources = {nonterm: new_sources[nonterm].nvals for nonterm in self.grammar.nonterms}

            # Iterate through all complex rules
            for l, r1, r2 in self.index.grammar.complex_rules:
                # l -> r1 r2 ==> index[l] += (new[l_src] * index[r1]) * index[r2] =>

                # 1) new[r1_src] += {(j, j) : (j, j) in new[l_src] and not in index[r1_src]}
                for i, _, _ in new_sources[l]:
                    if (i, i) not in self.index.sources[r1]:
                        new_sources[r1][i, i] = True

                # 2) tmp = new[l_src] * index[r1]
                tmp = new_sources[l] @ self.index.nonterms[r1]

                # 3) new[r2_src] += {(j, j) : (i, j) in tmp and not in index[r2_src]}
                update_sources_opt(tmp, self.index.sources[r2], new_sources[r2])

                # 4) index[l] += tmp * index[r2]
                self.index.nonterms[l] += tmp @ self.index.nonterms[r2]

            # Number of instances after operation
            new_nnz_nonterms = {nonterm: self.index.nonterms[nonterm].nvals for nonterm in self.grammar.nonterms}
            new_nnz_sources = {nonterm: new_sources[nonterm].nvals for nonterm in self.grammar.nonterms}

            # Update changed flag
            changed |= (not (old_nnz_nonterms == new_nnz_nonterms)) or (not (old_nnz_sources == new_nnz_sources))

        return self.index.nonterms[self.index.grammar.start_nonterm]
