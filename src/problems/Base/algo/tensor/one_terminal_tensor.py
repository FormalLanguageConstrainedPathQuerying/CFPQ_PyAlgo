from pathlib import Path

from pygraphblas import Matrix, BOOL, Scalar

from src.grammar.one_term_rsa import TemplateRSA
from src.graph.one_terminal_graph import OneTerminalGraph
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


class OneTerminalTensorAlgo:
    graph: OneTerminalGraph

    def prepare(self, graph: Path, templ_rsa_path: Path):
        templ_rsa = TemplateRSA.from_file(templ_rsa_path)
        self.graph = OneTerminalGraph(graph, templ_rsa, with_back_edges=True)

    def solve(self):
        element_type = self.graph.adjacency_matrix.type
        graph_size = self.graph.adjacency_matrix.nrows
        sizeKron = graph_size * self.graph.rsa.matrix.nrows

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

            # if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
            #     break

        thunk: Scalar = Scalar.from_type(self.graph.adjacency_matrix.type)
        thunk[0] = self.graph.rsa.nonterm_to_num['PointsTo'] << (self.graph.type_size - 2)
        return ResultAlgo(self.graph.adjacency_matrix.select(self.graph.nonterm_selector, thunk).pattern(), iter)

    def prepare_for_solve(self):
        pass
