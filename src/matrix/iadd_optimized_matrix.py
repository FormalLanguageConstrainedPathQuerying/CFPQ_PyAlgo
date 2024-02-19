import graphblas
from graphblas.core.matrix import Matrix

from src.matrix.abstract_enhanced_matrix_decorator import AbstractEnhancedMatrixDecorator
from src.matrix.enhanced_matrix import EnhancedMatrix


class IAddOptimizedMatrix(AbstractEnhancedMatrixDecorator):
    def __init__(self, base: EnhancedMatrix, nvals_factor: int = 10, min_nvals: int = 10):
        assert min_nvals > 0
        assert nvals_factor > 0
        self.matrices = [base]
        self.size_factor = nvals_factor
        self.min_size = min_nvals

    @property
    def base(self) -> EnhancedMatrix:
        return self.matrices[0]

    @property
    def nvals(self) -> int:
        return sum(m.nvals for m in self.matrices)

    def _map_and_fold(
            self,
            mapper,
            self_combine_threshold,
            combiner=lambda acc, cur: acc.ewise_add(
                cur,
                # FIXME bool specific code
                op=graphblas.monoid.any
            ).new(),
            acc=None,
            reverse_sort=False,
    ) -> Matrix:
        new_matrices = []
        for m in sorted(self.matrices, key=lambda m: m.nvals):
            if m.nvals <= self_combine_threshold and len(new_matrices) > 0:
                # print("self_combine:", new_matrices[-1].nvals, m.nvals, self_combine_threshold)
                new_matrices[-1] += m.to_matrix()
            else:
                new_matrices.append(m)
        self.matrices = new_matrices

        # TODO check OPTIMIZE_EMPTY
        for cur in sorted((mapper(m) for m in self.matrices if m.nvals != 0), key=lambda m: m.nvals, reverse=reverse_sort):
            acc = cur if acc is None else combiner(acc, cur)
        return mapper(self.base) if acc is None else acc

    def to_matrix(self) -> Matrix:
        # res = self._map_and_fold()
        # self.matrices = [self.base.enhance_similarly(res)]
        # print(list(sorted([m.nvals for m in self.matrices])))
        return self._map_and_fold(mapper=lambda m: m.to_matrix(), self_combine_threshold=float("inf"))
        # if len(self.matrices) > 1
        # # TODO this .dup() looks like a hack, although same can said about almost any dup(), redesign needed.
        # #  Best idea rn is to introduce some DupMatrix that dupes lazily when it (or original) gets modified.
        # else self.matrices[0].to_matrix().dup())

    def mxm(self, other: Matrix, *args, **kwargs) -> Matrix:
        return self._map_and_fold(mapper=lambda m: m.mxm(other, *args, **kwargs), self_combine_threshold=other.nvals)

    def r_complimentary_mask(self, other) -> Matrix:
        return self._map_and_fold(
            acc=other,
            reverse_sort=True,
            mapper=lambda m: m,
            combiner=lambda acc, cur: cur.r_complimentary_mask(acc),
            self_combine_threshold=other.nvals
        )

    def iadd(self, other: Matrix):
        # TODO lazy
        other = other.dup()
        if self.format is not None:
            other.ss.config["format"] = self.format
        base = self.base
        while True:
            other_nvals = max(other.nvals, self.min_size)
            # TODO choose closest fitting matrix, not just any
            # def get_size_diff(self_matrix_idx: int) -> int:
            #     self_matrix_nvals = max(self.matrices[self_matrix_idx].nvals, self.min_size)
            #     return max(other_nvals / self_matrix_nvals, self_matrix_nvals / other_nvals)

            # i = min((i for i in range(len(self.matrices))), key=get_size_diff, default=None)
            # if i is not None and get_size_diff(i) > self.size_factor:
            #     i = None

            i = next((i for i in range(len(self.matrices)) if
                      other_nvals / self.size_factor <= max(self.min_size,
                                                            self.matrices[i].nvals) <= other_nvals * self.size_factor),
                     None)

            if i is None:
                # self.matrices.append(self.base.create_similar(other))
                self.matrices.append(base.enhance_similarly(other))
                # self.dups.append(other.dup())
                return self
            other << other.ewise_add(
                self.matrices[i].to_matrix(),
                # FIXME bool specific code
                op=graphblas.monoid.any
            )
            del self.matrices[i]

    def enhance_similarly(self, base: Matrix) -> EnhancedMatrix:
        return IAddOptimizedMatrix(
            self.base.enhance_similarly(base),
            nvals_factor=self.size_factor,
            min_nvals=self.min_size
        )

    def __sizeof__(self):
        return sum(m.__sizeof__() for m in self.matrices)
