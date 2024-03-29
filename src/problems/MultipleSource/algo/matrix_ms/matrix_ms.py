from typing import Iterable
from pyformlang.cfg import CFG
from src.graph.graph import Graph

from pygraphblas import Matrix, descriptor
from pygraphblas.types import BOOL

from src.grammar.cnf_grammar import CnfGrammar
from src.graph.label_graph import LabelGraph
from src.problems.MultipleSource.MultipleSource import MultipleSourceProblem
from src.problems.utils import ResultAlgo


def update_sources(m: Matrix, dst: Matrix):
    """ dst += {(j, j) : (i, j) in m} by GrB_reduce src to a vector """

    # Transpose src and reduce to a vector
    J, V = m.T.reduce_vector(BOOL.ANY_MONOID).to_lists()

    # If j-th column of src contains True then add (j, j) to dst
    for k in range(len(J)):
        if V[k] is True:
            dst[J[k], J[k]] = True


def update_sources_opt(m: Matrix, mask: Matrix, res: Matrix):
    """ res += {(j, j): (i, j) in m and (j, j) not in mask}"""
    src_vec = m.reduce_vector(BOOL.ANY_MONOID, desc=descriptor.T0)
    for i, _ in src_vec:
        if (i, i) not in mask:
            res[i, i] = 1


def init_simple_rules(rules, graph: Graph):
    nonterms = LabelGraph(graph.matrices_size)
    for l, r in rules:
        nonterms[l] += graph[r]

    return nonterms


class MatrixMSBruteAlgo(MultipleSourceProblem):

    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

        self.sources = LabelGraph(self.graph.matrices_size)

        # Initialize simple rules
        self.__initial_nonterminals = init_simple_rules(self.grammar.simple_rules, self.graph)

    def clear_src(self):
        for label in self.sources.matrices:
            self.sources[label].clear()

    def solve(self, sources: Iterable):
        # Creating new index per solve call
        # index = SingleSourceIndex(self.graph, self.grammar)

        nonterminals = self.__initial_nonterminals.clone()

        # Initialize sources and nonterms nnz
        # nnz: (l, r1, r2) in complex rules -> (nnz(l), nnz(r1), nnz(r2))
        nnz = {}
        for l, r1, r2 in self.grammar.complex_rules:
            nnz[(l, r1, r2)] = (0, nonterminals[r1].nvals, nonterminals[r2].nvals)

        # Initialize source matrices masks
        m_src = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
        for v in sources:
            m_src[v, v] = True
            self.sources[self.grammar.start_nonterm][v, v] = True

        # Create temporary matrix
        tmp = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)

        # Algo's body
        iter = 0
        changed = True
        while changed:
            iter += 1
            changed = False

            # Number of instances before operation
            # old_nnz_nonterms = {nonterm: index.nonterms[nonterm].nvals for nonterm in index.grammar.nonterms}
            # old_nnz_sources = {nonterm: index.sources[nonterm].nvals for nonterm in index.grammar.nonterms}

            # Iterate through all complex rules
            for l, r1, r2 in self.grammar.complex_rules:
                new_nnz = self.sources[l].nvals, nonterminals[r1].nvals, nonterminals[r2].nvals
                if nnz[(l, r1, r2)] != new_nnz:
                    # 1) r1_src += {(j, j) : (i, j) \in l_src}
                    update_sources(self.sources[l], self.sources[r1])

                    # 2) tmp = l_src * r1
                    tmp = self.sources[l].mxm(nonterminals[r1], semiring=BOOL.ANY_PAIR)

                    # 3) r2_src += {(j, j) : (i, j) \in tmp}
                    update_sources(tmp, self.sources[r2])

                    # 4) l += tmp * r2
                    nonterminals[l] += tmp.mxm(nonterminals[r2], semiring=BOOL.ANY_PAIR)

                    # update nnz
                    nnz[(l, r1, r2)] = self.sources[l].nvals, nonterminals[r1].nvals, nonterminals[r2].nvals
                    changed = True

        return ResultAlgo(m_src.mxm(nonterminals[self.grammar.start_nonterm], semiring=BOOL.ANY_PAIR), iter), \
               nonterminals[self.grammar.start_nonterm]


class MatrixMSOptAlgo(MultipleSourceProblem):
    def prepare(self, graph: Graph, grammar: CFG):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = CnfGrammar.from_cfg(grammar)

        self.sources = LabelGraph(self.graph.matrices_size)
        self.nonterminals = init_simple_rules(self.grammar.simple_rules, self.graph)

    def clear_src(self):
        for label in self.sources.matrices:
            self.sources[label].clear()

    def solve(self, sources: Iterable):
        new_sources = LabelGraph(self.graph.matrices_size)

        # Initialize sources and nonterms nnz
        # nnz: (l, r1, r2) in complex rules -> (nnz(new[l]), nnz(index[r1]), nnz(index[r2]))
        nnz = {}
        for l, r1, r2 in self.grammar.complex_rules:
            nnz[(l, r1, r2)] = (0, self.nonterminals[r1].nvals, self.nonterminals[r2].nvals)

        # Initialize source matrices masks
        m_src = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
        for i in sources:
            m_src[i, i] = True
            if (i, i) not in self.sources[self.grammar.start_nonterm]:
                new_sources[self.grammar.start_nonterm][i, i] = True

        # Create temporary matrix
        tmp = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)

        # Algo's body
        changed = True
        iter = 0
        while changed:
            iter += 1
            changed = False

            # Iterate through all complex rules
            for l, r1, r2 in self.grammar.complex_rules:
                # l -> r1 r2 ==> index[l] += (new[l_src] * index[r1]) * index[r2]

                new_nnz = new_sources[l].nvals, self.nonterminals[r1].nvals, self.nonterminals[r2].nvals
                if nnz[(l, r1, r2)] != new_nnz:
                    # 1) new[r1_src] += {(j, j) : (j, j) in new[l_src] and not in index[r1_src]}
                    for i, _, _ in new_sources[l]:
                        if (i, i) not in self.sources[r1]:
                            new_sources[r1][i, i] = True

                    # 2) tmp = new[l_src] * index[r1]
                    new_sources[l].mxm(self.nonterminals[r1], out=tmp, semiring=BOOL.ANY_PAIR)

                    # 3) new[r2_src] += {(j, j) : (i, j) in tmp and not in index[r2_src]}
                    update_sources_opt(tmp, self.sources[r2], new_sources[r2])

                    # 4) index[l] += tmp * index[r2]
                    self.nonterminals[l] += tmp.mxm(self.nonterminals[r2], semiring=BOOL.ANY_PAIR)

                    # update nnz
                    nnz[(l, r1, r2)] = new_sources[l].nvals, self.nonterminals[r1].nvals, self.nonterminals[r2].nvals
                    changed = True
        for n in self.grammar.nonterms:
            self.sources[n] += new_sources[n]
        return ResultAlgo(m_src.mxm(self.nonterminals[self.grammar.start_nonterm], semiring=BOOL.ANY_PAIR), iter), \
               self.nonterminals[self.grammar.start_nonterm]
