import ctypes
import ctypes.util
import os.path
from pathlib import Path

from src.problems.AllPaths.AllPaths import AllPathsProblem

PATH_TO_SO = Path('src/problems/AllPaths/algo/matrix_all_paths/impl')


class LibBuilder:
    def __init__(self):
        if not os.path.isfile(PATH_TO_SO.joinpath('libAllPaths.so')):
            raise Exception("Please run the command 'make' in src/problems/AllPaths/algo/matrix_all_paths/impl")

        self.lib = ctypes.CDLL(str(PATH_TO_SO.joinpath('libAllPaths.so')))
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


class MatrixAlgo(AllPathsProblem):

    def prepare(self, graph: Path, grammar: Path):
        lib_builder = LibBuilder()
        self.lib = lib_builder.lib
        self.grammar = self.lib.grammar_new(str(grammar.rename(grammar.with_suffix(".cnf"))).encode('utf-8'))
        self.graph = self.lib.graph_new(str(graph.rename(graph.with_suffix(".txt"))).encode('utf-8'))

    def __del__(self):
        if self.grammar:
            self.lib.grammar_del(self.grammar)
        if self.graph:
            self.lib.graph_del(self.graph)
        self.lib.graphblas_finalize()

    def get_grammar(self):
        return self.grammar

    def solve(self):
        self.lib.intersect(self.grammar, self.graph)

    def getPaths(self, v_start, v_finish, nonterminal, max_len):
        return self.lib.getpaths(self.grammar, v_start, v_finish, nonterminal.encode('utf-8'), max_len)

    def get_elements(self, label):
        elements = self.lib.get_elements(self.grammar, label.encode('utf-8'))
        result = ctypes.cast(elements, ctypes.c_char_p).value
        self.lib.string_del(elements)
        return result.decode('utf-8')
