import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <terminals count> <output file>")
        sys.exit()
    fields_count = int(sys.argv[1])
    output_path = sys.argv[2]

    # f - field: load_f, store_f, load_f_r, store_f_r ; assign, assign_r, alloc, alloc_r, PT, FT, Al
    matricies_count = fields_count * 4 + 4 + 3
    states_count = 7
    edges = { 
        'alloc': [(0, 1)],
        'assign': [(0, 0)],
        'alloc_r': [(2, 3)],
        'assign_r': [(3, 3)],
        'PT': [(4, 5)],
        'FT': [(5, 6)],
        'Al': []
    }
    start_vertices = { 'PT': 0, 'FT': 2, 'Al': 4 }
    final_vertices = { 'PT': 1, 'FT': 3, 'Al': 6 }
    for field in range(fields_count):
        if not edges.get(f'load_{field}'):
            edges[f'load_{field}'] = []
        edges[f'load_{field}'].append((0,states_count))
        edges[f'Al'].append((states_count, states_count + 1))
        if not edges.get(f'store_{field}'):
            edges[f'store_{field}'] = []
        edges[f'store_{field}'].append((states_count + 1, 0))

        states_count += 2
        if not edges.get(f'store_{field}_r'):
            edges[f'store_{field}_r'] = []
        edges[f'store_{field}_r'].append((3, states_count))
        edges[f'Al'].append((states_count, states_count + 1))
        if not edges.get(f'load_{field}_r'):
            edges[f'load_{field}_r'] = []
        edges[f'load_{field}_r'].append((states_count + 1, 3))
        states_count += 2
    with open(output_path, "w") as f:
        f.write(f"{matricies_count}\n3\n{states_count}\n")
        for label in edges:
            f.write(f"{label}\n{len(edges[label])}\n")
            for v_from, v_to in edges[label]:
                f.write(f"{v_from} {v_to}\n")
        for nonterminal in ['PT', 'FT', 'Al']:
            f.write(f"{nonterminal}\n1\n")
            f.write(f"{start_vertices[nonterminal]} {final_vertices[nonterminal]}\n")


