from typing import Dict, Tuple, List, Callable
from pygraphblas import Matrix
from src.grammar.one_term_rsa import TemplateRSA, OneTerminalRSA
import re


class OneTerminalGraph:
    vertices_count: int
    rsa: OneTerminalRSA
    adjacency_matrix: Matrix

    def __init__(self,
                 vertices_count: int,
                 matrix_size: int,
                 edges: List[Tuple[int, int, int]],
                 rsa: OneTerminalRSA) -> None:
        """
        Initialize graph.

        """
        self.vertices_count = vertices_count
        self.rsa = rsa
        self.adjacency_matrix = Matrix.sparse(self.rsa.matrix.type, matrix_size, matrix_size)
        for from_s, value, to_s in edges:
            self.adjacency_matrix[from_s, to_s] = value

    def set_epsilon_nonterms(self):
        matrix_type = self.adjacency_matrix.type
        size = self.adjacency_matrix.nrows
        for nonterm in self.rsa.nonterm_via_eps:
            id_mat = Matrix.identity(matrix_type, size, self.rsa.nonterm_to_matrix(nonterm))
            with matrix_type.BOR:
                self.adjacency_matrix += id_mat

    @classmethod
    def _get_rsa(cls, templ_rsa, terms_num, terminals_to_num):
        return OneTerminalRSA.from_template_rsa(templ_rsa, terms_num, terminals_to_num)

    @classmethod
    def from_file(cls,
                  graph_path,
                  templ_rsa: TemplateRSA,
                  process_multiedge: Callable[
                      [int, str, int, Dict[Tuple[int, int], str], int], Tuple[Dict[Tuple[int, int], str], int]
                  ],
                  add_back_edges: bool = True):
        """
        OneTerminalGraph from a file with a list of edges and a TemplateRSA

        @param graph_path: path to the graph
        @param templ_rsa: template recursive state automaton
        @param process_multiedge: function to handle multiple edges in a graph
        @param add_back_edges: whether to add back edges to the graph

        @return: initialized OneTerminalGraph
        """
        vertices = set()
        terminal_to_num = dict()
        term_num = 1
        terms_num = set()
        edges = []
        with open(graph_path, 'r') as f:
            for line in f.readlines():
                v_from, terminal, v_to = line.split(' ')
                v_from, v_to = int(v_from), int(v_to)
                num_in_term = re.findall(r'\d+', terminal)
                count_num_in_term = len(num_in_term)
                if count_num_in_term == 1:
                    terms_num.add(int(num_in_term[0]))
                elif count_num_in_term > 1:
                    raise Exception("Incorrect terminal format")
                vertices.add(v_from)
                vertices.add(v_to)
                edges.append((v_from, terminal, v_to))
                if terminal not in terminal_to_num:
                    terminal_to_num[terminal] = term_num
                    term_num += 1
                if add_back_edges:
                    back_term = f'{terminal}_r'
                    if back_term not in terminal_to_num:
                        terminal_to_num[back_term] = term_num
                        term_num += 1

        vertices_count = max(vertices) + 1
        matrix_size = vertices_count
        one_terminal_edges: Dict[Tuple[int, int], str] = dict()
        for v_from, terminal, v_to in edges:
            if (v_from, v_to) in one_terminal_edges or v_from == v_to:
                one_terminal_edges, matrix_size = process_multiedge(v_from, terminal, v_to,
                                                                    one_terminal_edges,
                                                                    matrix_size)
            else:
                one_terminal_edges[(v_from, v_to)] = terminal
                if add_back_edges:
                    one_terminal_edges[(v_to, v_from)] = f'{terminal}_r'

        rsa = cls._get_rsa(templ_rsa, terms_num, terminal_to_num)
        return cls(vertices_count,
                   matrix_size,
                   [(from_v, terminal_to_num[label], to_v) for (from_v, to_v), label in one_terminal_edges.items()],
                   rsa)
