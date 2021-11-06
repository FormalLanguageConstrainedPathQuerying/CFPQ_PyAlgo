from pygraphblas import binary_op, types, select_op, Matrix
from src.grammar.one_term_rsa import OnetermRSA, TemplateRSA
import re

NONTERMINAL_MASK_INT32 = 0x80000000
MAX_TERMINALS_COUNT_INT32 = 0x7fffffff

NONTERMINAL_MASK_INT64 = 0x8000000000000000
MAX_TERMINALS_COUNT_INT64 = 0x7fffffffffffff


# PointsTo   -> (assign | load_[f] Alias store_[f]) alloc
# PointsTo_r -> alloc_r (assign_r | store_[f]_r A load_[f]_r)
# Alias      -> PointsTo PointsTo_r


class OneTerminalGraph():
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
        terminals_to_num = dict()
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
                if term not in terminals_to_num:
                    terminals_to_num[term] = term_num
                    term_num += 1
                if with_back_edges:
                    back_term = f'{term}_r'
                    edges.append((v_to, back_term, v_from))
                    if back_term not in terminals_to_num:
                        terminals_to_num[back_term] = term_num
                        term_num += 1

        vertices_count = len(vertices)
        terminals_count = len(terminals_to_num)

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
        elif terminals_count <= 2 ** (32 - 2):
            element_type = types.UINT32
            self.type_size = 32
            self.element_times = self.JAVATIMES32
        elif terminals_count <= 2 ** (64 - 2):
            element_type = types.UINT64
            self.type_size = 64
            self.element_times = self.JAVATIMES64
        else:
            # TODO Raise exception: too many terminals
            pass
            # raise

        self.adjacency_matrix = Matrix.sparse(
            element_type, vertices_count, vertices_count)

        self.rsa = OnetermRSA(templ_rsa, element_type, self.type_size, terms_num, terminals_to_num)

        for from_s, label, to_s in edges:
            self.adjacency_matrix[from_s, to_s] = terminals_to_num[label]

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

    def set_edge_term(self, v_from: int, v_to: int, terminal) -> None:
        """
        Set graph edge label terminal.

        @param v_from: edge start vertex
        @param v_to: edge end vertex
        @param terminal: edge label terminal
        """
        self.adjacency_matrix[v_from, v_to] = (self.adjacency_matrix[v_from, v_to] & self._nonterminal_mask) | \
                                              self._terminals[terminal]

    def set_edge_nonterm(self, v_from: int, v_to: int, nonterminal: int) -> None:
        """
        Add nonterminal to graph edge label.

        @param v_from: edge start vertex
        @param v_to: edge end vertex
        @param nonterminal: edge label nonterminal
        """
        self.adjacency_matrix[v_from, v_to] |= 1 << (self.type_size - self._nonterminals[nonterminal])
