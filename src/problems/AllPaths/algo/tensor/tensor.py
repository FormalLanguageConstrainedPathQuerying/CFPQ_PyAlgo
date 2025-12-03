from pathlib import Path
from cfpq_data import RSM
from pyformlang.cfg import CFG
from pygraphblas import Matrix, BOOL, Vector, descriptor, INT64
from src.graph.graph import Graph
from typing import Iterable, Union
import sys

from src.grammar.rsa import RecursiveAutomaton
from src.graph.label_graph import LabelGraph
from src.problems.AllPaths.algo.tensor.tensor_path import TensorPathsNew
from src.problems.AllPaths.algo.tensor.tensor_extract_subgraph import TensorExtractSubGraph

from src.problems.AllPaths.AllPaths import AllPathsProblem

from src.problems.utils import ResultAlgo


def restore_eps_paths(nonterminals: Iterable, graph: Graph):
    for label in nonterminals:
        for i in range(graph.matrices_size):
            graph[label][i, i] = True


# def transitive_closure(m: Matrix):
#     prev = -1
#     while prev != m.nvals:
#         prev = m.nvals
#         with BOOL.ANY_PAIR, Accum(BOOL.ANY):
#             m @= m

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

def msbfs(kron: Matrix, front: Matrix):
    visited = front.dup()
    # print("visited")
    # print(visited)
    current_front = front.dup()
    # print("current_front")
    # print(current_front)
    # print("kron in msbfs")
    # print(kron)
    while current_front.nvals > 0:
        with BOOL.ANY_PAIR:
            new_front = current_front @ kron
        # print("new front")
        # print(new_front)
        with BOOL.LOR_LAND:
            # C = A.apply(gb.INT64.ONE, mask=B, desc=gb.descriptor.RSC)
            current_front = new_front.apply(INT64.ONE,mask=visited, desc=descriptor.RSC)
        # print("current front 2")
        # print(current_front)
        with BOOL.LOR:
            visited += current_front
            # print("visited")
            # print(visited)
    
    return visited

def ms_bfs(sources: Matrix, kron: Matrix, visited: Matrix):
    with BOOL.ANY_PAIR:
        front = visited @ sources
        while front.nvals > 0:
            new_front = front.mxm(kron)
            front = new_front.union(visited, mask=visited, desc=descriptor.C)
            visited += front

def msbfs_vis(kron: Matrix, front: Matrix, visited: Matrix):
    # print("visited")
    # print(visited)
    current_front = front.dup()
    # print("current_front")
    # print(current_front)
    # print("kron in msbfs")
    # print(kron)
    # while current_front.nvals > 0:
    #     with BOOL.ANY_PAIR:
    #         new_front = current_front @ kron
    #     # print("new front")
    #     # print(new_front)
    #     with BOOL.LOR_LAND:
    #         # C = A.apply(gb.INT64.ONE, mask=B, desc=gb.descriptor.RSC)
    #         current_front = new_front.apply(INT64.ONE,mask=visited, desc=descriptor.RSC)
    #     # print("current front 2")
    #     # print(current_front)
    #     with BOOL.LOR:
    #         visited += current_front
    #         # print("visited")
    #         # print(visited)
    while current_front.nvals > 0:
            new_front = current_front.mxm(kron)
            current_front = new_front.union(visited, mask=visited, desc=descriptor.C)
            visited += current_front
    
    return visited


class TensorSimpleAlgo(AllPathsProblem):


    def prepare(self, graph: Graph, grammar: Union[RSM, CFG, Path]):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = RecursiveAutomaton.from_grammar_or_path(grammar)

    def solve(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        iter = 0
        changed = True
        while changed:
            iter += 1
            changed = False

            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
            for label in self.grammar.labels:
                kron += self.grammar[label].kronecker(self.graph[label])

            front = self.grammar
            
            transitive_closure(kron)

            # update
            for nonterminal in self.grammar.nonterminals:
                control_sum = self.graph[nonterminal].nvals
                for element in self.grammar.states[nonterminal]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    self.graph[nonterminal] += kron[start_i:start_i + self.graph.matrices_size - 1,
                            start_j:start_j + self.graph.matrices_size - 1]

                new_control_sum = self.graph[nonterminal].nvals

                if new_control_sum != control_sum:
                    changed = True

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)
    
    def solve_msbfs(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        iter = 0
        changed = True
        # print("\ngrammar:\n")
        # print(self.grammar.matrices_size)
        # for label in self.grammar.labels:
                # print(label)
                # print(self.grammar[label])

        # print("\ngraph:\n")
        # print(self.graph.matrices_size)
        # for k in self.graph.matrices:
            # print(k)
            # print(self.graph.matrices[k])      

        while changed:
            iter += 1
            changed = False

            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
            for label in self.grammar.labels:
                kron += self.grammar[label].kronecker(self.graph[label])
            # print("KRON")
            # print(kron)

            num_start_rows = len(self.grammar.start_state) * self.graph.matrices_size
            front = Matrix.sparse(BOOL, num_start_rows, sizeKron)

            row_id = 0
            # start = dict()
            # self.grammar.start_state = {'S':1}
            # print("CFG start symbol:", self.grammar.start_nonterm)
            # print("Automaton start states:", self.grammar.start_state)
            # print("Front matrix size:", num_start_rows, "x", sizeKron)

            for nonterm, p in self.grammar.start_state.items():
                # print(f"Processing nonterminal: {nonterm}, state: {p}")в
                for g in range(self.graph.matrices_size):
                    # print("p,g,size:",p,g,self.graph.matrices_size )
                    kron_row = p  *self.graph.matrices_size + g
                    # print(f"  Taking row {kron_row} from Kronecker matrix")
                    for col_idx in kron[kron_row].indices:
                        front[row_id, col_idx] = True
                    
                    row_id += 1

            # print(f"Final front matrix: {front.nrows} x {front.ncols}")
            # print(f"Non-zero elements in front: {front.nvals}")
            # print("front")
            # print(front)
            print(front.nrows)
            # nfront = kron.dup()
            res = msbfs(kron,front)
            # print("res")
            # print(res)
            # print("done")
            # transitive_closure(kron)

            state_to_front_index = {}
            for front_index, (start_nonterm, start_state) in enumerate(self.grammar.start_state.items()):
                state_to_front_index[start_state] = front_index

            for nonterminal in self.grammar.nonterminals:
                control_sum = self.graph[nonterminal].nvals

                for i, j in self.grammar.states[nonterminal]:

                    if i not in state_to_front_index:
                        continue
                        
                    front_index = state_to_front_index[i]
                    start_i = front_index * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size
                    
                    self.graph[nonterminal] += res[
                        start_i : (front_index + 1) * self.graph.matrices_size-1,
                        start_j : start_j + self.graph.matrices_size-1
                    ]

                if self.graph[nonterminal].nvals != control_sum:
                    changed = True

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)

 

    def prepare_for_solve(self):
        for label in self.grammar.nonterminals:
            self.graph[label].clear()

    def prepare_for_exctract_paths(self):
        sizeKron = self.graph.matrices_size * self.grammar.matrices_size
        self.kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        for label in self.grammar.labels:
            self.kron += self.grammar[label].kronecker(self.graph[label])

    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        return TensorPathsNew(self.graph, self.grammar, self.kron).get_paths(v_start, v_finish, nonterminal, max_len)

    def get_sub_graph(self, v_start: int, v_finish: int, nonterminal: str, max_high: int):
        return TensorExtractSubGraph(self.graph, self.grammar, self.kron, max_high).get_sub_graph(v_start,
                                                                                                  v_finish,
                                                                                                  nonterminal)


class TensorDynamicAlgo(AllPathsProblem):

    def prepare(self, graph: Graph, grammar: Union[RSM, CFG, Path]):
        self.graph = graph
        self.graph.load_bool_graph()
        self.grammar = RecursiveAutomaton.from_grammar_or_path(grammar)

    def solve(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        sizeKron = self.graph.matrices_size * self.grammar.matrices_size
        # assert(false)
        prev_kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        iter = 0
        block = LabelGraph(self.graph.matrices_size)
        changed = True
        first_iter = True
        while changed:
            changed = False
            iter += 1

            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)

            if first_iter:
                for label in self.grammar.labels:
                    kron += self.grammar[label].kronecker(self.graph[label])
            else:
                for nonterminal in block.matrices:
                    kron += self.grammar[nonterminal].kronecker(block[nonterminal])
                    # print("block of nonterm", nonterminal)
                    # print(block[nonterminal])
                    block[nonterminal] = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
            # print("KRON")
            # print(kron)
            transitive_closure(kron)
            # print("kron after TC")
            # print(kron)

            if not first_iter:
                part = prev_kron.mxm(kron, semiring=BOOL.ANY_PAIR)
                # print("part")
                # print(part)
                # print("prev_kron first")
                # print(prev_kron)
                with BOOL.ANY_PAIR:
                    kron += prev_kron + part @ prev_kron + part + kron @ prev_kron

            prev_kron = kron
            # print("kron after smth")
            # print(kron)
            # print("prev kron")
            # print(prev_kron)

            for nonterminal in self.grammar.nonterminals:
                control_sum = self.graph[nonterminal].nvals
                for element in self.grammar.states[nonterminal]:
                    i = element[0]
                    j = element[1]

                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size

                    # block[nonterminal] += kron[start_i:start_i + self.graph.matrices_size - 1,
                    #                       start_j:start_j + self.graph.matrices_size - 1]
                    if first_iter:
                        block[nonterminal] += kron[start_i:start_i + self.graph.matrices_size - 1,
                                                  start_j:start_j + self.graph.matrices_size - 1]
                    else:
                        new_edges = kron[start_i:start_i + self.graph.matrices_size - 1,
                                         start_j:start_j + self.graph.matrices_size - 1]
                        part = new_edges - block[nonterminal]
                        block[nonterminal] += part.select('==', True)

                self.graph[nonterminal] += block[nonterminal]
                new_control_sum = self.graph[nonterminal].nvals

                if new_control_sum != control_sum:
                    changed = True

            first_iter = False

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)

    def solve_msbfs(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)

        graph_size = self.graph.matrices_size
        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        prev_kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        iter = 0
        block = LabelGraph(self.graph.matrices_size)
        changed = True
        first_iter = True
        start_states = [self.grammar.start_state[nonterm] for nonterm in self.grammar.nonterminals]
        while changed:
            changed = False
            iter += 1

            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)

            if first_iter:
                for label in self.grammar.labels:
                    kron += self.grammar[label].kronecker(self.graph[label])
                graph_diag = Matrix.from_diag(Vector.dense(BOOL, graph_size, fill=True))
                ms_bfs_sources = Matrix.sparse(BOOL, nrows=kron.ncols, ncols=kron.ncols)
                for v in start_states:
                    start = v * graph_size
                    ms_bfs_sources[start: start + graph_size - 1, start:start + graph_size - 1] = graph_diag
                ms_bfs_visited = ms_bfs_sources.dup()
                ms_bfs(ms_bfs_sources, kron, ms_bfs_visited)
                prev_kron = kron
                visited_updates = ms_bfs_visited.dup()

            else:
                for nonterminal in block.matrices:
                    kron += self.grammar[nonterminal].kronecker(block[nonterminal])
                    block[nonterminal] = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
                ms_bfs_sources = Matrix.from_diag(kron.reduce_vector())
                with BOOL.ANY_PAIR:
                    kron = prev_kron + kron
                visited_updates = ms_bfs_visited.dup()
                ms_bfs(ms_bfs_sources, kron, ms_bfs_visited)
                visited_updates = (ms_bfs_visited - visited_updates).nonzero()
                prev_kron = kron

            for nonterminal in self.grammar.nonterminals:
                control_sum = self.graph[nonterminal].nvals
                for element in self.grammar.states[nonterminal]:
                    i = element[0]
                    j = element[1]
                    start_i = i * self.graph.matrices_size
                    start_j = j * self.graph.matrices_size
                    block[nonterminal] += visited_updates[start_i:start_i + self.graph.matrices_size - 1,
                                            start_j:start_j + self.graph.matrices_size - 1]
                self.graph[nonterminal] += block[nonterminal]
                new_control_sum = self.graph[nonterminal].nvals

                if new_control_sum != control_sum:
                    changed = True

            first_iter = False

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)   
    
    def solve_msbfs_bad(self):
        restore_eps_paths(self.grammar.start_and_finish, self.graph)
        sizeKron = self.graph.matrices_size * self.grammar.matrices_size

        prev_kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        iter = 0
        block = LabelGraph(self.graph.matrices_size)
        changed = True
        first_iter = True
        
        num_start_rows = len(self.grammar.start_state) * self.graph.matrices_size
        visited = Matrix.sparse(BOOL, num_start_rows, sizeKron)
        # print("\ngrammar:\n")
        # print(self.grammar.matrices_size)
        # for label in self.grammar.labels:
        #         print(label)
        #         print(self.grammar[label])

        # print("\ngraph:\n")
        # print(self.graph.matrices_size)
        # for k in self.graph.matrices:
        #     print(k)
        #     print(self.graph.matrices[k])    
        while changed:
            changed = False
            iter += 1

            kron = Matrix.sparse(BOOL, sizeKron, sizeKron)

            if first_iter:
                for label in self.grammar.labels:
                    kron += self.grammar[label].kronecker(self.graph[label])
            else:
                for nonterminal in block.matrices:
                    kron += self.grammar[nonterminal].kronecker(block[nonterminal])
                    # print("block of nonterm", nonterminal)
                    # print(block[nonterminal])
                    block[nonterminal] = Matrix.sparse(BOOL, self.graph.matrices_size, self.graph.matrices_size)
            # print("KRON")
            # print(kron)
            front = Matrix.sparse(BOOL, num_start_rows, sizeKron)
            
            
            if first_iter:
                row_id = 0
                # print("CFG start symbol:", self.grammar.start_nonterm)
                # print("Automaton start states:", self.grammar.start_state)
                # print("Front matrix size:", num_start_rows, "x", sizeKron)
                # assert(false)
                for nonterm, p in self.grammar.start_state.items():
                    # print(f"Processing nonterminal: {nonterm}, state: {p}")
                    for g in range(self.graph.matrices_size):
                        # print("p,g,size:",p,g,self.graph.matrices_size )
                        kron_row = p  *self.graph.matrices_size + g
                        # print(f"  Taking row {kron_row} from Kronecker matrix")
                        for col_idx in kron[kron_row].indices:
                            front[row_id, col_idx] = True
                        
                        row_id += 1
            else:
                # редьюсим вправо. получаем  вектор где ненулевые значения на нужных индексах
                reduced_kron = Vector.sparse(BOOL,sizeKron)
                kron.reduce_vector(out=reduced_kron)
                # строим диагональную по этому вектору
                diag = Matrix.from_diag(reduced_kron)
                # старый visited умножаем VIS x DIAG
                
                # получили новый фронт. 
                front = visited.mxm(diag,semiring=BOOL.ANY_PAIR)

            # print(f"Final front matrix: {front.nrows} x {front.ncols}")
            # print(f"Non-zero elements in front: {front.nvals}")
            # print("front")
            # print(front)
            # print(front.nrows)
            if first_iter:
                visited = front.dup()

            # print("vis")
            # print(visited)
            # тут делаем копию старого виситеда
            prev_visited = visited.dup()
            kron += prev_kron
            res = msbfs_vis(kron,front,visited) 
            # print("res") 
            # print(res)  
            # transitive_closure(kron)
            visited = res.dup()
            visited_dif = visited.apply(INT64.ONE, mask=prev_visited, desc=descriptor.C)     
            # print("visited_dif")
            # print(visited_dif)
            
            # for nonterminal in self.grammar.nonterminals:
            #     control_sum = self.graph[nonterminal].nvals
            #     for i, j in self.grammar.states[nonterminal]:

            #         if i not in state_to_front_index:
            #             continue
                        
            #         front_index = state_to_front_index[i]
            #         start_i = i * self.graph.matrices_size
            #         start_j = j * self.graph.matrices_size
            #         print("k i:",i)
            #         print("k j:",j)
            #         print("k start_i:",start_i)
            #         print("k start_j:",start_j)
            #         print("k end_i:",(front_index+1)*self.graph.matrices_size - 1)
            #         print("k end_j:", start_j + self.graph.matrices_size - 1)
            #         kron[
            #             start_i : (i + 1) * self.graph.matrices_size-1,
            #             :
            #         ] += res[
            #             start_i : (front_index + 1) * self.graph.matrices_size-1,
            #             :
            #         ]
            # prev_kron = kron
            
            # print("kron after smth")
            # print(kron)
            # print("PREV__KRON")
            # print(prev_kron)
            
            prev_kron = kron
            state_to_front_index = {}
            for front_index, (start_nonterm, start_state) in enumerate(self.grammar.start_state.items()):
                state_to_front_index[start_state] = front_index
            # ниже вытаскиваем значения из разницы двух visited
            for nonterminal in self.grammar.nonterminals:
                control_sum = self.graph[nonterminal].nvals
               
                for i,j in self.grammar.states[nonterminal]:
                    front_index = state_to_front_index[i]
                    start_i = front_index*self.graph.matrices_size
                    start_j = j * self.graph.matrices_size
                    # print("i:",i)
                    # print("j:",j)
                    # print("start_i:",start_i)
                    # print("start_j:",start_j)
                    # print("end_i:",(front_index+1)*self.graph.matrices_size - 1)
                    # print("end_j:", start_j + self.graph.matrices_size - 1)
                    # block[nonterminal] += res[start_i:start_i + self.graph.matrices_size - 1,
                    #                       start_j:start_j + self.graph.matrices_size - 1]
                    for n in self.grammar.finish_states[nonterminal]:
                        # print("n", n)
                        # print(n * self.grammar.matrices_size)
                        # print( n * self.grammar.matrices_size + self.graph.matrices_size - 1)

                        # if first_iter:
                        block[nonterminal] += visited_dif[start_i:(front_index+1)*self.graph.matrices_size - 1,
                                                        n * self.graph.matrices_size : n * self.graph.matrices_size + self.graph.matrices_size - 1]
                        # else:
                        #     new_edges = visited_dif[start_i:(front_index+1)*self.graph.matrices_size - 1,
                        #                         n * self.graph.matrix_size :n * self.graph.matrix_size  + self.graph.matrices_size - 1]
                        #     part = new_edges - block[nonterminal]
                        #     block[nonterminal] += part.select('==', True)

                self.graph[nonterminal] += block[nonterminal]
                new_control_sum = self.graph[nonterminal].nvals

                if new_control_sum != control_sum:
                    changed = True

            first_iter = False

            if self.grammar.nonterminals.isdisjoint(self.grammar.labels):
                break

        return ResultAlgo(self.graph[self.grammar.start_nonterm], iter)


    def prepare_for_solve(self):
        for label in self.grammar.nonterminals:
            self.graph[label].clear()

    def prepare_for_exctract_paths(self):
        sizeKron = self.graph.matrices_size * self.grammar.matrices_size
        self.kron = Matrix.sparse(BOOL, sizeKron, sizeKron)
        for label in self.grammar.labels:
            self.kron += self.grammar[label].kronecker(self.graph[label])

    def getPaths(self, v_start: int, v_finish: int, nonterminal: str, max_len: int):
        return TensorPathsNew(self.graph, self.grammar, self.kron).get_paths(v_start, v_finish, nonterminal, max_len)

    def get_sub_graph(self, v_start: int, v_finish: int, nonterminal: str, max_high: int):
        return TensorExtractSubGraph(self.graph, self.grammar, self.kron, max_high).get_sub_graph(v_start,
                                                                                                  v_finish,
                                                                                                  nonterminal)
