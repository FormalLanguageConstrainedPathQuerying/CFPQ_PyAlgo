from pygraphblas import Matrix, BOOL, Scalar

from src.graph.one_terminal_graph import OneTerminalGraph
from src.problems.utils import ResultAlgo
from src.problems.AllPaths.algo.tensor.tensor import transitive_closure


class OneTerminalTensorAlgo:

    def solve(self, start_nonterm: str, graph: OneTerminalGraph):
        """
        Solve reachability problem for start_nonterm with tensor algorithm

        @param start_nonterm: Start nonterminal in RSA
        @param graph: OneTerminalGraph for which it is necessary to solve reachability problem

        @return: matrix with information about reachable vertices and the number of iterations of the algorithm,
        packed in ResultAlgo
        """
        rsa = graph.rsa

        element_type = graph.adjacency_matrix.type
        graph_size = graph.adjacency_matrix.nrows

        graph.set_epsilon_nonterms()
        iter = 0
        changed = True
        while changed:
            iter += 1
            changed = False

            kron = rsa.matrix.kronecker(graph.adjacency_matrix,
                                        op=rsa.times_op,
                                        cast=BOOL)

            transitive_closure(kron)
            
            # update
            for nonterm in rsa.nonterm_to_num:
                start = rsa.start_state[nonterm]
                block = Matrix.sparse(BOOL, graph_size, graph_size)
                for finish in rsa.finish_states[nonterm]:
                    start_i = start * graph_size
                    start_j = finish * graph_size

                    block += kron[start_i:start_i + graph_size - 1, start_j:start_j + graph_size - 1]

                new_block = Matrix.sparse(element_type, graph_size, graph_size)
                block.cast(element_type).apply_first(rsa.nonterm_to_matrix(nonterm),
                                                     element_type.TIMES,
                                                     out=new_block)

                with element_type.BOR:
                    new_graph: Matrix = graph.adjacency_matrix + new_block

                if new_graph.isne(graph.adjacency_matrix):
                    graph.adjacency_matrix = new_graph
                    changed = True

        thunk: Scalar = Scalar.from_type(element_type)
        thunk[0] = rsa.nonterm_to_matrix(start_nonterm)
        return ResultAlgo(graph.adjacency_matrix
                          .extract_matrix(slice(0, graph.vertices_count - 1),
                                          slice(0, graph.vertices_count - 1))
                          .select(rsa.select_op, thunk)
                          .pattern(),
                          iter)


class OneTerminalDynamicTensorAlgo(OneTerminalTensorAlgo):

    def solve(self, start_nonterm: str, graph: OneTerminalGraph):
        """
        Solve reachability problem for start_nonterm with incremental tensor algorithm

        @param start_nonterm: Start nonterminal in RSA
        @param graph: OneTerminalGraph for which it is necessary to solve reachability problem

        @return: matrix with information about reachable vertices and the number of iterations of the algorithm,
        packed in ResultAlgo
        """
        rsa = graph.rsa
        element_type = graph.adjacency_matrix.type
        graph_size = graph.adjacency_matrix.nrows

        graph.set_epsilon_nonterms()

        changed = True
        iter = 0
        first_iter = True

        updates = Matrix.sparse(element_type, graph_size, graph_size)
        while changed:
            changed = False
            iter += 1

            if first_iter:
                kron = rsa.matrix.kronecker(graph.adjacency_matrix,
                                            op=rsa.times_op,
                                            cast=BOOL)
                transitive_closure(kron)
                prev_kron = kron
                kron_updates = kron
            else:
                kron = rsa.matrix.kronecker(updates,
                                            op=rsa.times_op,
                                            cast=BOOL)
                updates = Matrix.sparse(element_type, graph_size, graph_size)
                with BOOL.ANY_PAIR:
                    kron = prev_kron + kron
                transitive_closure(kron)
                kron_updates = (kron - prev_kron).nonzero()
                prev_kron = kron

            # update
            for nonterm in rsa.nonterm_to_num:
                block = Matrix.sparse(BOOL, graph_size, graph_size)
                start = rsa.start_state[nonterm]
                for finish in rsa.finish_states[nonterm]:
                    start_i = start * graph_size
                    start_j = finish * graph_size

                    block += kron_updates[start_i:start_i + graph_size - 1, start_j:start_j + graph_size - 1]

                with element_type.BOR:
                    updates += block.cast(element_type).apply_first(
                        rsa.nonterm_to_matrix(nonterm), element_type.TIMES)
            if updates.nvals > 0:
                with element_type.BOR:
                    graph.adjacency_matrix = graph.adjacency_matrix + updates
                changed = True

            first_iter = False

        thunk: Scalar = Scalar.from_type(graph.adjacency_matrix.type)
        thunk[0] = rsa.nonterm_to_matrix(start_nonterm)
        return ResultAlgo(graph.adjacency_matrix
                          .extract_matrix(slice(graph.vertices_count - 1),
                                          slice(graph.vertices_count - 1))
                          .select(rsa.select_op, thunk)
                          .pattern(),
                          iter)
