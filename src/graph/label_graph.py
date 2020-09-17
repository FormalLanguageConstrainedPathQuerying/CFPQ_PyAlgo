from pygraphblas.matrix import Matrix
from pygraphblas.types import BOOL
from tqdm import tqdm

from src.utils.common import chunkify


class LabelGraph:
    def __init__(self, matrices_size, number_edges):
        self.matrices = {}
        self.matrices_size = matrices_size
	self.number_edges = number_edges

    def __getitem__(self, item: str) -> Matrix:
        if item not in self.matrices:
            self.matrices[item] = Matrix.sparse(BOOL, self.matrices_size, self.matrices_size)
        return self.matrices[item]

    def __setitem__(self, key, value):
        self.matrices[key] = value

    def __iter__(self):
        return self.matrices.__iter__()

    def get_number_of_vertices(self):
	return self.matrices_size

    def get_number_of_edges(self):
	return self.number_edges

    @classmethod
    def from_txt(cls, path, verbose=False):
        triplets = list()
	size_matrices = 0
	number_edges = 0
        with open(path, 'r') as f:
            for line in tqdm(f.readlines()) if verbose else f.readlines():

		number_edges += 1
				
                v, label, to = line.split()
                v, to = int(v), int(to)
                size_matrices = max(size_matrices, v, to)
				
		triplets.append((v, label, to))

		g = LabelGraph(size_matrices + 1, number_edges)
		
		for triplet in triplets:
 		    g[triplet[1]][triplet[0], triplet[2]] = True

        return g

    def chunkify(self, chunk_len) -> list:
        return list(chunkify(list(range(self.matrices_size)), chunk_len))

