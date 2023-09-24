class AccumMatrix:
    def __init__(self, base, min_size, format=0):
        self.base = base
        self.min_size = min_size
        self.format = format

        self.matrices = []

    def __iadd__(self, other):
        if other.nvals == 0:
            return self
        while True:
            other.format = self.format
            other_nvals = max(other.nvals, self.min_size)
            i = next((i for i in range(len(self.matrices)) if
                      other_nvals / self.base <= max(self.min_size, self.matrices[i].nvals) <= other_nvals * self.base),
                     None)
            if i is None:
                self.matrices.append(other.dup())
                return self
            m = self.matrices[i]
            del self.matrices[i]
            m += other
            other = m

    def map_and_fold(self, fmap=lambda m: m, combine=lambda acc, cur: acc + cur):
        acc = None
        for cur in sorted((fmap(m) for m in self.matrices), key=lambda m: m.nvals):
            acc = cur if acc is None else combine(acc, cur)
        return acc

    @property
    def nvals(self):
        return sum([m.nvals for m in self.matrices])
