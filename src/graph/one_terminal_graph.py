from typing import Dict, Tuple

from pygraphblas import binary_op, types, select_op, Matrix
from src.grammar.one_term_rsa import OneTerminalOneNonterminalRSA, TemplateRSA, OneTerminalRSA
import re

NONTERMINAL_MASK_INT32 = 0x80000000
MAX_TERMINALS_COUNT_INT32 = 0x7fffffff

NONTERMINAL_MASK_INT64 = 0x8000000000000000
MAX_TERMINALS_COUNT_INT64 = 0x7fffffffffffff


# PointsTo   -> (assign | load_[f] Alias store_[f]) alloc
# PointsTo_r -> alloc_r (assign_r | store_[f]_r A load_[f]_r)
# Alias      -> PointsTo PointsTo_r


class OneTerminalOneNonterminalGraph:
    """
    TODO: Add description for this graph labels representation
    """

    def __init__(self, graph_path, templ_rsa: TemplateRSA, with_back_edges: bool = True) -> None:
        """
        Initialize graph.

        @param vertices_count: graph vertices count, it's required to initialize the adjacency matrix 
        @param nonterminals: it's required to define nonterminal mask select matrix elements type 
        @param terminals: it's required to select matrix elements type
        """
        nonterminals_count = len(templ_rsa.start_state)

        vertices = set()
        self.terminals_to_num = dict()
        term_num = 1
        terms_num = set()
        edges = []
        with open(graph_path, 'r') as f:
            # for line in tqdm(f.readlines()) if verbose else f.readlines():
            for line in f.readlines():
                v_from, term, v_to = line.split(', ')
                v_from, v_to = int(v_from), int(v_to)
                num_in_term = re.findall(r'\d+', term)
                count_num_in_term = len(num_in_term)
                if count_num_in_term == 1:
                    terms_num.add(int(num_in_term[0]))
                elif count_num_in_term > 1:
                    pass  # TODO raise error
                vertices.add(v_from)
                vertices.add(v_to)
                edges.append((v_from, term, v_to))
                if term not in self.terminals_to_num:
                    self.terminals_to_num[term] = term_num
                    term_num += 1
                back_term = f'{term}_r'
                if back_term not in self.terminals_to_num:
                    self.terminals_to_num[back_term] = term_num
                    term_num += 1

        vertices_count = len(vertices)
        self.base_graph_size = vertices_count
        one_terminal_edges: Dict[Tuple[int, int], str] = dict()
        for v_from, terminal, v_to in edges:
            if (v_from, v_to) in one_terminal_edges:
                v_new = vertices_count
                vertices.add(v_new)
                vertices_count += 1
                if terminal.startswith("store"):
                    one_terminal_edges[(v_from, v_new)] = terminal
                    one_terminal_edges[(v_new, v_from)] = f'{terminal}_r'
                    one_terminal_edges[(v_new, v_to)] = "assign"
                    one_terminal_edges[(v_to, v_new)] = "assign_r"
                else:
                    one_terminal_edges[(v_from, v_new)] = "assign"
                    one_terminal_edges[(v_new, v_from)] = "assign_r"
                    one_terminal_edges[(v_new, v_to)] = terminal
                    one_terminal_edges[(v_to, v_new)] = f'{terminal}_r'
            else:
                one_terminal_edges[(v_from, v_to)] = terminal
                one_terminal_edges[(v_to, v_from)] = f'{terminal}_r'

        edges = None
        terminals_count = len(self.terminals_to_num)

        self._nonterminal_mask = 0
        if terminals_count <= 2 ** (8 - 2):
            element_type = types.UINT8
            self.type_size = 8
            self.element_times = self.JAVATIMES8
            self.nonterm_selector = self.JAVASELECTOR8
        elif terminals_count <= 2 ** (16 - 2):
            element_type = types.UINT16
            self.type_size = 16
            self.element_times = self.JAVATIMES16
            self.nonterm_selector = self.JAVASELECTOR16
        elif terminals_count <= 2 ** (32 - 2):
            element_type = types.UINT32
            self.type_size = 32
            self.element_times = self.JAVATIMES32
            self.nonterm_selector = self.JAVASELECTOR32
        elif terminals_count <= 2 ** (64 - 2):
            element_type = types.UINT64
            self.type_size = 64
            self.element_times = self.JAVATIMES64
            self.nonterm_selector = self.JAVASELECTOR64
        else:
            # TODO Raise exception: too many terminals
            pass
            # raise

        self.adjacency_matrix = Matrix.sparse(
            element_type, vertices_count, vertices_count)

        self.rsa = OneTerminalOneNonterminalRSA(templ_rsa, element_type, self.type_size, terms_num, self.terminals_to_num)

        # for v_from, label, v_to in edges:
        for (v_from, v_to), terminal in one_terminal_edges.items():
            self.adjacency_matrix[v_from, v_to] = self.terminals_to_num[terminal]

    @binary_op(types.UINT8)
    def JAVATIMES8(x, y):
        term_mask = 0x3f
        nonterm_mask = 0xff - term_mask
        return ((x & nonterm_mask) == (y & nonterm_mask) and (x & nonterm_mask != 0)) or \
               ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT8, types.UINT8)
    def JAVASELECTOR8(i, j, x, v):
        nonterm_mask = 0xff - 0x3f
        return x & nonterm_mask == v

    @binary_op(types.UINT16)
    def JAVATIMES16(x, y):
        term_mask = 0x3fff
        nonterm_mask = 0xffff - term_mask
        return ((x & nonterm_mask) == (y & nonterm_mask) and (x & nonterm_mask != 0)) or \
               ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT16, types.UINT16)
    def JAVASELECTOR16(i, j, x, v):
        nonterm_mask = 0xffff - 0x3fff
        return x & nonterm_mask == v

    @binary_op(types.UINT32)
    def JAVATIMES32(x, y):
        term_mask = 0x3fffffff
        nonterm_mask = 0xffffffff - term_mask
        return ((x & nonterm_mask) == (y & nonterm_mask) and (x & nonterm_mask != 0)) or \
               ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT32, types.UINT32)
    def JAVASELECTOR32(i, j, x, v):
        nonterm_mask = 0xffffffff - 0x3fffffff
        return x & nonterm_mask == v

    @binary_op(types.UINT64)
    def JAVATIMES64(x, y):
        term_mask = 0x3fffffffffffffff
        nonterm_mask = 0xffffffffffffffff - term_mask
        return ((x & nonterm_mask) == (y & nonterm_mask) and (x & nonterm_mask != 0)) or \
               ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT64, types.UINT64)
    def JAVASELECTOR64(i, j, x, v):
        nonterm_mask = 0xffffffffffffffff - 0x3fffffffffffffff
        return x & nonterm_mask == v


class OneTerminalGraph:
    """
    TODO: Add description for this graph labels representation
    """

    def __init__(self, graph_path, templ_rsa: TemplateRSA, with_back_edges: bool = True) -> None:
        """
        Initialize graph.

        """
        nonterminals_count = len(templ_rsa.start_state)

        vertices = set()
        self.terminals_to_num = dict()
        term_num = 1
        terms_num = set()
        edges = []
        with open(graph_path, 'r') as f:
            # for line in tqdm(f.readlines()) if verbose else f.readlines():
            for line in f.readlines():
                v_from, term, v_to = line.split(', ')
                v_from, v_to = int(v_from), int(v_to)
                num_in_term = re.findall(r'\d+', term)
                count_num_in_term = len(num_in_term)
                if count_num_in_term == 1:
                    terms_num.add(int(num_in_term[0]))
                elif count_num_in_term > 1:
                    pass  # TODO raise error
                vertices.add(v_from)
                vertices.add(v_to)
                edges.append((v_from, term, v_to))
                if term not in self.terminals_to_num:
                    self.terminals_to_num[term] = term_num
                    term_num += 1
                if with_back_edges:
                    back_term = f'{term}_r'
                    edges.append((v_to, back_term, v_from))
                    if back_term not in self.terminals_to_num:
                        self.terminals_to_num[back_term] = term_num
                        term_num += 1

        vertices_count = len(vertices)
        terminals_count = len(self.terminals_to_num)

        self._nonterminal_mask = 0
        if terminals_count <= 2 ** (8 - 3):
            element_type = types.UINT8
            self.type_size = 8
            self.element_times = self.JAVATIMES8
            self.nonterm_selector = self.JAVASELECTOR8
        elif terminals_count <= 2 ** (16 - 3):
            element_type = types.UINT16
            self.type_size = 16
            self.element_times = self.JAVATIMES16
            self.nonterm_selector = self.JAVASELECTOR16
        elif terminals_count <= 2 ** (32 - 3):
            element_type = types.UINT32
            self.type_size = 32
            self.element_times = self.JAVATIMES32
            self.nonterm_selector = self.JAVASELECTOR32
        elif terminals_count <= 2 ** (64 - 3):
            element_type = types.UINT64
            self.type_size = 64
            self.element_times = self.JAVATIMES64
            self.nonterm_selector = self.JAVASELECTOR64
        else:
            # TODO Raise exception: too many terminals
            pass
            # raise

        self.adjacency_matrix = Matrix.sparse(
            element_type, vertices_count, vertices_count)

        self.rsa = OneTerminalRSA(templ_rsa, element_type, self.type_size, terms_num, self.terminals_to_num)

        for from_s, label, to_s in edges:
            self.adjacency_matrix[from_s, to_s] = self.terminals_to_num[label]

    def set_epsilon_nonterms(self):
        matrix_type = self.adjacency_matrix.type
        size = self.adjacency_matrix.nrows
        for nonterm in self.rsa.nonterm_via_eps:
            id_mat = Matrix.identity(matrix_type, size,
                                     1 << (self.type_size - 3 + self.rsa.nonterm_to_num[nonterm] - 1))
            with matrix_type.BOR:
                self.adjacency_matrix += id_mat

    @binary_op(types.UINT8)
    def JAVATIMES8(x, y):
        term_mask = 0x1f
        nonterm_mask = 0xff - term_mask
        return (x & y & nonterm_mask) or ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT8, types.UINT8)
    def JAVASELECTOR8(i, j, x, v):
        nonterm_mask = 0xff - 0x1f
        return x & nonterm_mask & v

    @binary_op(types.UINT16)
    def JAVATIMES16(x, y):
        term_mask = 0x1fff
        nonterm_mask = 0xffff - term_mask
        return (x & y & nonterm_mask) or ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT16, types.UINT16)
    def JAVASELECTOR16(i, j, x, v):
        nonterm_mask = 0xffff - 0x1fff
        return x & nonterm_mask & v

    @binary_op(types.UINT32)
    def JAVATIMES32(x, y):
        term_mask = 0x1fffffff
        nonterm_mask = 0xffffffff - term_mask
        return (x & y & nonterm_mask) or ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT32, types.UINT32)
    def JAVASELECTOR32(i, j, x, v):
        nonterm_mask = 0xffffffff - 0x3fffffff
        return x & nonterm_mask & v

    @binary_op(types.UINT64)
    def JAVATIMES64(x, y):
        term_mask = 0x1fffffffffffffff
        nonterm_mask = 0xffffffffffffffff - term_mask
        return (x & y & nonterm_mask) or ((x & term_mask) == (y & term_mask) and (x & term_mask != 0))

    @select_op(types.UINT64, types.UINT64)
    def JAVASELECTOR64(i, j, x, v):
        nonterm_mask = 0xffffffffffffffff - 0x1fffffffffffffff
        return x & nonterm_mask & v

