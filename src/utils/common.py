def chunkify(xs, chunk_size):
    for i in range(0, len(xs), chunk_size):
        yield xs[i:i+chunk_size]
