import ctypes
import ctypes.util


class LibBuilder:
    def __init__(self):

        self.lib = ctypes.CDLL('src/algo/matrix_all_paths/impl/libAllPaths.so')
        LP_c_char = ctypes.POINTER(ctypes.c_char)
        self.lib.grammar_new.argtypes = [LP_c_char]
        self.lib.grammar_new.restype = ctypes.c_void_p

        self.lib.grammar_del.argtypes = [ctypes.c_void_p]

        self.lib.graph_new.argtypes = [LP_c_char]
        self.lib.graph_new.restype = ctypes.c_void_p

        self.lib.graph_del.argtypes = [ctypes.c_void_p]

        self.lib.intersect.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.lib.get_elements.argtypes = [ctypes.c_void_p, LP_c_char]
        self.lib.get_elements.restype = ctypes.c_void_p

        self.lib.string_del.argtypes = [ctypes.c_void_p]

        self.lib.getpaths.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, LP_c_char, ctypes.c_int]
        self.lib.getpaths.restype = ctypes.c_int
        self.lib.graphblas_init()

    def get_lib(self):
        return self.lib


class MatrixAllPaths:
    def __init__(self, graph: str, grammar: str):
        lib_builder = LibBuilder()
        self.lib = lib_builder.get_lib()
        self.grammar = self.lib.grammar_new(grammar.encode('utf-8'))
        self.graph = self.lib.graph_new(graph.encode('utf-8'))

    def __del__(self):
        if self.grammar:
            self.lib.grammar_del(self.grammar)
        if self.graph:
            self.lib.graph_del(self.graph)
        self.lib.graphblas_finalize()

    def get_grammar(self):
        return self.grammar

    def create_index(self):
        if self.grammar:
            self.lib.grammar_del(self.grammar)
            self.grammar = None
        if self.graph:
            self.lib.graph_del(self.graph)
            self.graph = None

        self.lib.intersect(self.grammar, self.graph)

    def restore_paths(self, from_vertex, to_vertex, nonterm):
        return self.lib.getpaths(self.grammar, from_vertex, to_vertex, nonterm.encode('utf-8'), 0)

    def get_elements(self, label):
        elements = self.lib.get_elements(self.grammar, label.encode('utf-8'))
        result = ctypes.cast(elements, ctypes.c_char_p).value
        self.lib.string_del(elements)
        return result.decode('utf-8')
