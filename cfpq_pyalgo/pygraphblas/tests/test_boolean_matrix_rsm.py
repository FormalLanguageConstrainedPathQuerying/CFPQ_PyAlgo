from pyformlang.rsa import RecursiveAutomaton

import cfpq_pyalgo.pygraphblas as algo


def test_empty():
    rsa = RecursiveAutomaton.from_text("S -> epsilon")
    rsm = algo.BooleanMatrixRsm.from_rsa(rsa)

    assert rsm.nonterminals == {"S"}
    assert rsm.get_start_state("S") == 0
    assert rsm.get_final_states("S") == [0]
    assert rsm.matrices_size == 1


def test_a():
    rsa = RecursiveAutomaton.from_text("S -> a")
    rsm = algo.BooleanMatrixRsm.from_rsa(rsa)

    assert rsm.nonterminals == {"S"}
    assert rsm.labels == {"a"}
    assert len(rsm.get_final_states("S")) == 1
    start_state = rsm.get_start_state("S")
    final_state = rsm.get_final_states("S")[0]
    assert start_state == 1 - final_state
    assert rsm.matrices_size == 2
    assert rsm["a"].nvals == 1
    assert rsm["a"][start_state, final_state] == True


def test_ab():
    rsa = RecursiveAutomaton.from_text("S -> a b")
    rsm = algo.BooleanMatrixRsm.from_rsa(rsa)

    assert rsm.nonterminals == {"S"}
    assert rsm.labels == {"a", "b"}
    assert rsm.matrices_size == 3
    assert rsm["a"].nvals == 1
    assert rsm["b"].nvals == 1
    assert len(rsm.get_final_states("S")) == 1
    start_state = rsm.get_start_state("S")
    final_state = rsm.get_final_states("S")[0]
    a = rsm["a"].to_lists()
    b = rsm["b"].to_lists()
    assert start_state == a[0][0]
    assert a[1][0] == b[0][0]
    assert b[1][0] == final_state


def test_AB():
    rsa = RecursiveAutomaton.from_text(
        "S -> A B | epsilon\nA -> a | epsilon\nB -> b | epsilon"
    )
    rsm = algo.BooleanMatrixRsm.from_rsa(rsa)

    assert rsm.nonterminals == {"S", "A", "B"}
    assert rsm.labels == {"a", "b", "A", "B"}
    assert rsm.matrices_size == 7
    assert rsm["a"].nvals == 1
    assert rsm["b"].nvals == 1
    assert rsm["A"].nvals == 1
    assert rsm["B"].nvals == 1
    # S box
    assert len(rsm.get_final_states("S")) == 2
    start_state = rsm.get_start_state("S")
    final_states = rsm.get_final_states("S")
    assert start_state in final_states
    a = rsm["A"].to_lists()
    b = rsm["B"].to_lists()
    assert start_state == a[0][0]
    assert a[1][0] == b[0][0]
    assert b[1][0] in final_states
    # A box
    assert len(rsm.get_final_states("A")) == 2
    start_state = rsm.get_start_state("A")
    final_states = rsm.get_final_states("A")
    assert start_state in final_states
    a = rsm["a"].to_lists()
    assert start_state == a[0][0]
    assert a[1][0] in final_states
    # B box
    assert len(rsm.get_final_states("B")) == 2
    start_state = rsm.get_start_state("B")
    final_states = rsm.get_final_states("B")
    assert start_state in final_states
    b = rsm["b"].to_lists()
    assert start_state == b[0][0]
    assert b[1][0] in final_states


def test_SSaa():
    rsa = RecursiveAutomaton.from_text("S -> S a | a")
    rsm = algo.BooleanMatrixRsm.from_rsa(rsa)

    assert rsm.nonterminals == {"S"}
    assert rsm.labels == {"S", "a"}
    assert rsm.matrices_size == 3
    assert rsm["S"].nvals == 1
    assert rsm["a"].nvals == 2
    assert len(rsm.get_final_states("S")) == 1
    start_state = rsm.get_start_state("S")
    final_state = rsm.get_final_states("S")[0]
    assert rsm["a"][start_state, final_state]
    s = rsm["S"].to_lists()
    assert start_state == s[0][0]
    assert rsm["a"][s[1][0], final_state]
