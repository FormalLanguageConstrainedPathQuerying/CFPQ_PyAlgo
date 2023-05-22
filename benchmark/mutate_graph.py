def process_multiedge_ma(v_from, terminal, v_to, edges, graph_size):
    if (v_from, v_to) in edges:
        v_new = graph_size
        graph_size += 1
        edges[(v_from, v_new)] = "a"
        edges[(v_new, v_from)] = "a_r"
        edges[(v_new, v_to)] = terminal
        edges[(v_to, v_new)] = f'{terminal}_r'
    elif v_from == v_to:
        v_new_1 = graph_size
        v_new_2 = graph_size + 1
        graph_size += 2
        if terminal == "a":
            edges[(v_from, v_new_1)] = terminal
            edges[(v_new_1, v_from)] = f'{terminal}_r'
            edges[(v_new_1, v_new_2)] = "a"
            edges[(v_new_2, v_new_1)] = "a_r"
            edges[(v_new_2, v_to)] = "a"
            edges[(v_to, v_new_2)] = "a_r"
    return edges, graph_size


def process_multiedge_java(v_from, terminal, v_to, edges, graph_size):
    if (v_from, v_to) in edges:
        v_new = graph_size
        graph_size += 1
        if terminal.startswith("store"):
            edges[(v_from, v_new)] = terminal
            edges[(v_new, v_from)] = f'{terminal}_r'
            edges[(v_new, v_to)] = "assign"
            edges[(v_to, v_new)] = "assign_r"
        else:
            edges[(v_from, v_new)] = "assign"
            edges[(v_new, v_from)] = "assign_r"
            edges[(v_new, v_to)] = terminal
            edges[(v_to, v_new)] = f'{terminal}_r'
    elif v_from == v_to:
        v_new_1 = graph_size
        v_new_2 = graph_size + 1
        graph_size += 2
        if terminal.startswith("store"):
            edges[(v_from, v_new_1)] = terminal
            edges[(v_new_1, v_from)] = f'{terminal}_r'
            edges[(v_new_1, v_new_2)] = "assign"
            edges[(v_new_2, v_new_1)] = "assign_r"
            edges[(v_new_2, v_to)] = "assign"
            edges[(v_to, v_new_2)] = "assign_r"
        else:
            edges[(v_from, v_new_1)] = "assign"
            edges[(v_new_1, v_from)] = "assign_r"
            edges[(v_new_1, v_new_2)] = "assign"
            edges[(v_new_2, v_new_1)] = "assign_r"
            edges[(v_new_2, v_to)] = terminal
            edges[(v_to, v_new_2)] = f'{terminal}_r'
    return edges, graph_size
