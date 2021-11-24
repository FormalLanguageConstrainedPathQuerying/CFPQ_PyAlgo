from pyformlang.cfg import CFG, Production, Variable, Terminal

import cfpq_pyalgo.pygraphblas as algo


def test_empty():
    cfg = CFG.from_text("S -> epsilon")

    wcnf = algo.WCNF(cfg)

    assert wcnf.start_variable == Variable("S")
    assert wcnf.variables == [Variable("S")]
    assert wcnf.terminals == []
    assert wcnf.productions == [Production(Variable("S"), [])]
    assert wcnf.epsilon_productions == [Production(Variable("S"), [])]
    assert wcnf.unary_productions == []
    assert wcnf.binary_productions == []


def test_a():
    cfg = CFG.from_text("S -> a")

    wcnf = algo.WCNF(cfg)

    assert wcnf.start_variable == Variable("S")
    assert wcnf.variables == [Variable("S")]
    assert wcnf.terminals == [Terminal("a")]
    assert wcnf.productions == [Production(Variable("S"), [Terminal("a")])]
    assert wcnf.epsilon_productions == []
    assert wcnf.unary_productions == [Production(Variable("S"), [Terminal("a")])]
    assert wcnf.binary_productions == []


def test_ab():
    cfg = CFG.from_text("S -> a b")

    wcnf = algo.WCNF(cfg)

    assert wcnf.start_variable == Variable("S")
    assert wcnf.variables == [Variable("S"), Variable("a#CNF#"), Variable("b#CNF#")]
    assert wcnf.terminals == [Terminal("a"), Terminal("b")]
    assert wcnf.productions == [
        Production(Variable("S"), [Variable("a#CNF#"), Variable("b#CNF#")]),
        Production(Variable("a#CNF#"), [Terminal("a")]),
        Production(Variable("b#CNF#"), [Terminal("b")]),
    ]
    assert wcnf.epsilon_productions == []
    assert wcnf.unary_productions == [
        Production(Variable("a#CNF#"), [Terminal("a")]),
        Production(Variable("b#CNF#"), [Terminal("b")]),
    ]
    assert wcnf.binary_productions == [
        Production(Variable("S"), [Variable("a#CNF#"), Variable("b#CNF#")]),
    ]


def test_AB():
    cfg = CFG.from_text("S -> A B | epsilon\nA -> a | epsilon\nB -> b | epsilon")

    wcnf = algo.WCNF(cfg)

    assert wcnf.start_variable == Variable("S")
    assert wcnf.variables == [Variable("A"), Variable("B"), Variable("S")]
    assert wcnf.terminals == [Terminal("a"), Terminal("b")]
    assert wcnf.productions == [
        Production(Variable("A"), []),
        Production(Variable("A"), [Terminal("a")]),
        Production(Variable("B"), []),
        Production(Variable("B"), [Terminal("b")]),
        Production(Variable("S"), []),
        Production(Variable("S"), [Variable("A"), Variable("B")]),
    ]
    assert wcnf.epsilon_productions == [
        Production(Variable("A"), []),
        Production(Variable("B"), []),
        Production(Variable("S"), []),
    ]
    assert wcnf.unary_productions == [
        Production(Variable("A"), [Terminal("a")]),
        Production(Variable("B"), [Terminal("b")]),
    ]
    assert wcnf.binary_productions == [
        Production(Variable("S"), [Variable("A"), Variable("B")]),
    ]
