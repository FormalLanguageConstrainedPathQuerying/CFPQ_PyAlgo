from cfpq_model.cnf_grammar_template import CnfGrammarTemplate, Symbol
from cfpq_model.label_decomposed_graph import LabelDecomposedGraph


def explode_indices(
    graph: LabelDecomposedGraph,
    grammar: CnfGrammarTemplate
) -> (LabelDecomposedGraph, CnfGrammarTemplate):
    block_matrix_space = graph.block_matrix_space
    block_count = block_matrix_space.block_count

    matrices = dict()
    for symbol, matrix in graph.matrices.items():
        if block_matrix_space.is_single_cell(matrix.shape):
            matrices[symbol] = matrix
        else:
            for i, block in enumerate(block_matrix_space.get_hyper_vector_blocks(matrix)):
                matrices[_index_symbol(symbol, i)] = block

    epsilon_rules = []
    for non_terminal in grammar.epsilon_rules:
        if non_terminal.is_indexed:
            for i in range(block_count):
                epsilon_rules.append(_index_symbol(non_terminal, i))
        else:
            epsilon_rules.append(non_terminal)

    simple_rules = []
    for (non_terminal, terminal) in grammar.simple_rules:
        if non_terminal.is_indexed or terminal.is_indexed:
            for i in range(block_count):
                simple_rules.append((_index_symbol(non_terminal, i), _index_symbol(terminal, i)))
        else:
            simple_rules.append((non_terminal, terminal))

    complex_rules = []
    for (non_terminal, symbol1, symbol2) in grammar.complex_rules:
        if non_terminal.is_indexed or symbol1.is_indexed or symbol2.is_indexed:
            for i in range(block_count):
                complex_rules.append((
                    _index_symbol(non_terminal, i),
                    _index_symbol(symbol1, i),
                    _index_symbol(symbol2, i),
                ))
        else:
            complex_rules.append((non_terminal, symbol1, symbol2))

    return (
        LabelDecomposedGraph(
            vertex_count=graph.vertex_count,
            block_matrix_space=block_matrix_space,
            dtype=graph.dtype,
            matrices=matrices
        ),
        CnfGrammarTemplate(
            start_nonterm=grammar.start_nonterm,
            epsilon_rules=epsilon_rules,
            simple_rules=simple_rules,
            complex_rules=complex_rules
        )
    )


def _index_symbol(symbol: Symbol, index: int) -> Symbol:
    return Symbol(f"{symbol.label}_{index}") if symbol.is_indexed else symbol
