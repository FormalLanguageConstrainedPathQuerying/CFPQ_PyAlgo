def get_graph_size(path):
    res = -1
    with open(path, 'r') as f:
        for line in f.readlines():
            v, label, to = line.split()
            v, to = int(v), int(to)
            res = max(res, v, to)
    return res + 1
