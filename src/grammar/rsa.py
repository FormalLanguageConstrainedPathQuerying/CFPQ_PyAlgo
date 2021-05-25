from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL

from pathlib import Path

from pyformlang.cfg import CFG
from cfpq_data import rsm_from_text


class RecursiveAutomaton:
    """
    This class representing recursive state automaton. supports only the functions necessary for the algorithms to work
    """
    def __init__(self):
        self.labels = set()
        self.nonterminals = set()
        self.matrices = dict()
        self.states = dict()
        self.start_and_finish = set()
        self.matrices_size = 0
        self.start_state = dict()
        self.finish_states = dict()
        self.terminals = set()
        self.out_states = dict()

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(BOOL, self.matrices_size, self.matrices_size)

        return self.matrices[item]

    @classmethod
    def from_cfg(cls, cfg: CFG):
        grammar = cfg.to_text()

        productions = dict()
        for line in grammar.split("\n"):
            part_line = line.split(" -> ")
            right = part_line[1]
            if right == "":
                right = "epsilon"
            if part_line[0] in productions:
                productions[part_line[0]] += " | " + right
            else:
                productions[part_line[0]] = right

        grammar_new = ""
        for nonterminal in productions:
            grammar_new += nonterminal + " -> " + productions[nonterminal] + "\n"

        grammar_new = grammar_new[:-1]
        base_rsm = rsm_from_text(grammar_new)

        rsa = RecursiveAutomaton()
        current_state = 0
        mapping_state = dict()
        transtion_by_label = dict()
        for nonterm, dfa in base_rsm.boxes:
            rsa.nonterminals.add(nonterm)
            rsa.labels.union(dfa.symbols)
            for label in dfa.symbols:
                if label not in transtion_by_label:
                    transtion_by_label.update({label: []})

            dfa_dict = dfa.to_dict()
            for state in dfa_dict:
                if state not in mapping_state:
                    mapping_state[state] = current_state
                    current_state += 1

                for trans in dfa_dict[state]:
                    if dfa_dict[state][trans] not in mapping_state:
                        mapping_state[dfa_dict[state][trans]] = current_state
                        current_state += 1
                    transtion_by_label[trans].append((mapping_state[state], mapping_state[dfa_dict[state][trans]]))

        rsa.matrices_size = current_state
        for label in transtion_by_label:
            rsa.matrices[label] = Matrix.sparse(BOOL, rsa.matrices_size, rsa.matrices_size)
            for trans in transtion_by_label[label]:
                rsa.matrices[label][trans[0], trans[1]] = True

        for nonterm, dfa in base_rsm.boxes:
            rsa.states[nonterm] = Matrix.sparse(BOOL, rsa.matrices_size, rsa.matrices_size)
            for final_state in dfa.final_states:
                rsa.states[nonterm][mapping_state[dfa.start_state], mapping_state[final_state]] = True

        return rsa

    @classmethod
    def from_file(cls, path: Path):
        """
        Load RSA from file
        @param path: path to file with RSA
        @return: initialized class
        """
        rsa = RecursiveAutomaton()
        with open(path, "r") as file:
            count_matrix = int(file.readline())
            count_nonterminals = int(file.readline())
            matrices_size = int(file.readline())
            rsa.matrices_size = matrices_size

            for i in range(count_matrix):
                label = file.readline().replace("\n", "")
                rsa.labels.add(label)
                count_edge = int(file.readline())
                for j in range(count_edge):
                    first, second = file.readline().split()
                    rsa[label][int(first), int(second)] = True

                    if int(first) in rsa.out_states:
                        rsa.out_states[int(first)].append((int(second), label))
                    else:
                        rsa.out_states[int(first)] = [(int(second), label)]

            for i in range(count_nonterminals):
                label = file.readline().replace("\n", "")
                rsa.nonterminals.add(label)
                rsa.states.update({label: Matrix.sparse(BOOL, rsa.matrices_size, rsa.matrices_size)})
                count_edge = int(file.readline())
                for j in range(count_edge):
                    first, second = file.readline().split()
                    rsa.states[label][int(first), int(second)] = True
                    rsa.start_state.update({label: int(first)})
                    if label in rsa.finish_states:
                        rsa.finish_states[label].append(int(second))
                    else:
                        rsa.finish_states.update({label: [int(second)]})
                    if first == second:
                        rsa.start_and_finish.add(label)
        rsa.terminals = rsa.labels.difference(rsa.nonterminals)
        return rsa
