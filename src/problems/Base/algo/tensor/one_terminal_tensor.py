from pathlib import Path

from pygraphblas import Matrix, BOOL, Scalar

from src.grammar.one_term_rsa import TemplateRSA
from src.graph.label_graph import LabelGraph
from src.graph.one_terminal_graph import OneTerminalOneNonterminalGraph, OneTerminalGraph
from src.problems.utils import ResultAlgo


def transitive_closure(m: Matrix):
    prev = m.nvals
    degree = m
    with BOOL.ANY_PAIR:
        degree = degree @ m
        m += degree
    while prev != m.nvals:
        prev = m.nvals
        with BOOL.ANY_PAIR:
            degree = degree @ m
            m += degree


class OneTerminalOneNonterminalTensorAlgo:
    graph: OneTerminalOneNonterminalGraph

    def prepare(self, graph: Path, templ_rsa_path: Path):
        templ_rsa = TemplateRSA.from_file(templ_rsa_path)
        self.graph = OneTerminalOneNonterminalGraph(graph, templ_rsa, with_back_edges=True)

    def solve(self, start_nonterm: str):
        element_type = self.graph.adjacency_matrix.type
        graph_size = self.graph.adjacency_matrix.nrows

        iter = 0
        control_sum = self.graph.adjacency_matrix.select('>=', 1 << (self.graph.type_size - 2)).nonzero().nvals
        changed = True
        while changed:
            iter += 1
            changed = False

            kron = self.graph.rsa.matrix.kronecker(self.graph.adjacency_matrix, op=self.graph.element_times,
                                                   cast=BOOL).nonzero()

            transitive_closure(kron)

            # update
            for nonterminal, num in self.graph.rsa.nonterm_to_num.items():
                start = self.graph.rsa.start_state[nonterminal]
                for finish in self.graph.rsa.finish_states[nonterminal]:
                    start_i = start * graph_size
                    start_j = finish * graph_size

                    block = kron[start_i:start_i + graph_size - 1, start_j:start_j + graph_size - 1]

                    new_block = Matrix.sparse(element_type, graph_size, graph_size)
                    block.cast(element_type).apply_first(num << (self.graph.type_size - 2), element_type.TIMES,
                                                         out=new_block)

                    with element_type.BOR:
                        self.graph.adjacency_matrix += new_block

                    new_control_sum = self.graph.adjacency_matrix.select('>=', 1 << (
                            self.graph.type_size - 2)).nonzero().nvals

                    if new_control_sum != control_sum:
                        control_sum = new_control_sum
                        changed = True
            del kron

        thunk: Scalar = Scalar.from_type(self.graph.adjacency_matrix.type)
        thunk[0] = self.graph.rsa.nonterm_to_num[start_nonterm] << (self.graph.type_size - 2)
        return ResultAlgo(self.graph.adjacency_matrix
                          .extract_matrix(slice(0, self.graph.base_graph_size - 1), slice(0, self.graph.base_graph_size - 1))
                          .select(self.graph.nonterm_selector, thunk)
                          .pattern(),
                          iter)


class OneTerminalTensorAlgo:
    graph: OneTerminalGraph

    def prepare(self, graph: Path, templ_rsa_path: Path):
        templ_rsa = TemplateRSA.from_file(templ_rsa_path)
        self.graph = OneTerminalGraph(graph, templ_rsa, with_back_edges=False)

    def solve(self, start_nonterm: str):
        element_type = self.graph.adjacency_matrix.type
        graph_size = self.graph.adjacency_matrix.nrows

        self.graph.set_epsilon_nonterms()
        iter = 0
        changed = True
        while changed:
            iter += 1
            changed = False

            kron = self.graph.rsa.matrix.kronecker(self.graph.adjacency_matrix, op=self.graph.element_times,
                                                   cast=BOOL).nonzero()

            transitive_closure(kron)

            # update
            for nonterminal, num in self.graph.rsa.nonterm_to_num.items():
                start = self.graph.rsa.start_state[nonterminal]
                for finish in self.graph.rsa.finish_states[nonterminal]:
                    start_i = start * graph_size
                    start_j = finish * graph_size

                    block = kron[start_i:start_i + graph_size - 1, start_j:start_j + graph_size - 1]

                    new_block = Matrix.sparse(element_type, graph_size, graph_size)
                    block.cast(element_type).apply_first(1 << (self.graph.type_size - 3 + num - 1), element_type.TIMES,
                                                         out=new_block)

                    with element_type.BOR:
                        new_graph: Matrix = self.graph.adjacency_matrix + new_block

                    if new_graph.isne(self.graph.adjacency_matrix):
                        self.graph.adjacency_matrix = new_graph
                        changed = True

                    del new_graph
            del kron

        thunk: Scalar = Scalar.from_type(self.graph.adjacency_matrix.type)
        thunk[0] = 1 << (self.graph.type_size - 3 + self.graph.rsa.nonterm_to_num[start_nonterm] - 1)
        return ResultAlgo(self.graph.adjacency_matrix.select(self.graph.nonterm_selector, thunk).pattern(), iter)


class OneTerminalOneNonterminalDynamicTensorAlgo:
    graph: OneTerminalOneNonterminalGraph

    def prepare(self, graph: Path, templ_rsa_path: Path):
        templ_rsa = TemplateRSA.from_file(templ_rsa_path)
        self.graph = OneTerminalOneNonterminalGraph(graph, templ_rsa, with_back_edges=True)

    def solve(self, start_nonterm: str):
        element_type = self.graph.adjacency_matrix.type
        graph_size = self.graph.adjacency_matrix.nrows
        sizeKron = graph_size * self.graph.rsa.matrix.nrows
        prev_kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        block = LabelGraph(graph_size)

        changed = True
        iter = 0
        control_sum = self.graph.adjacency_matrix.select('>=', 1 << (self.graph.type_size - 2)).nonzero().nvals
        first_iter = True
        updates = Matrix.sparse(element_type, graph_size, graph_size)
        while changed:
            changed = False
            iter += 1

            if first_iter:
                kron = self.graph.rsa.matrix.kronecker(self.graph.adjacency_matrix, op=self.graph.element_times,
                                                       cast=BOOL).nonzero()
                transitive_closure(kron)
            else:
                # kron = self.graph.rsa.matrix.kronecker(self.graph.adjacency_matrix, op=self.graph.element_times,
                #                                        cast=BOOL).nonzero()
                kron += self.graph.rsa.matrix.kronecker(updates, op=self.graph.element_times,
                                                       cast=BOOL).nonzero()
                updates = Matrix.sparse(element_type, graph_size, graph_size)
                # for nonterminal in block.matrices:
                #     block[nonterminal] = Matrix.sparse(BOOL, graph_size, graph_size)

            # transitive_closure(kron)

            if not first_iter:
                part = prev_kron.mxm(kron, semiring=BOOL.ANY_PAIR)
                with BOOL.ANY_PAIR:
                    kron += prev_kron + part @ prev_kron + part + kron @ prev_kron

            prev_kron = kron

            # update
            for nonterminal, num in self.graph.rsa.nonterm_to_num.items():
                block[nonterminal] = Matrix.sparse(BOOL, graph_size, graph_size)
                start = self.graph.rsa.start_state[nonterminal]
                for finish in self.graph.rsa.finish_states[nonterminal]:
                    start_i = start * graph_size
                    start_j = finish * graph_size

                    if first_iter:
                        block[nonterminal] += kron[start_i:start_i + graph_size - 1, start_j:start_j + graph_size - 1]
                    else:
                        new_edges = kron[start_i:start_i + graph_size - 1, start_j:start_j + graph_size - 1]
                        part = new_edges - block[nonterminal]
                        block[nonterminal] += part.select('==', True)

                with element_type.BOR:
                    updates += block[nonterminal].cast(element_type).apply_first(num << (self.graph.type_size - 2),
                                                                                 element_type.TIMES)
            with element_type.BOR:
                self.graph.adjacency_matrix += updates

            new_control_sum = self.graph.adjacency_matrix.select('>=', 1 << (
                    self.graph.type_size - 2)).nonzero().nvals

            if new_control_sum != control_sum:
                control_sum = new_control_sum
                changed = True

        thunk: Scalar = Scalar.from_type(self.graph.adjacency_matrix.type)
        thunk[0] = self.graph.rsa.nonterm_to_num[start_nonterm] << (self.graph.type_size - 2)
        return ResultAlgo(self.graph.adjacency_matrix
                          .extract_matrix(slice(self.graph.base_graph_size), slice(self.graph.base_graph_size))
                          .select(self.graph.nonterm_selector, thunk)
                          .pattern(),
                          iter)
