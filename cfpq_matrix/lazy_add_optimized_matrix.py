from graphblas.core.matrix import Matrix
from graphblas.core.operator import Monoid, Semiring

from cfpq_matrix.abstract_optimized_matrix_decorator import AbstractOptimizedMatrixDecorator
from cfpq_matrix.optimized_matrix import OptimizedMatrix
from cfpq_matrix.subtractable_semiring import SubOp


class LazyAddOptimizedMatrix(AbstractOptimizedMatrixDecorator):
    def __init__(self, base: OptimizedMatrix, nvals_factor: int = 10, min_nvals: int = 10):
        assert min_nvals > 0
        assert nvals_factor > 0
        self.matrices = [base]
        self.size_factor = nvals_factor
        self.min_size = min_nvals
        self.last_used_monoid = None

    @property
    def base(self) -> OptimizedMatrix:
        return self.matrices[0]

    @property
    def nvals(self) -> int:
        return sum(m.nvals for m in self.matrices)

    def _map_and_fold(
            self,
            mapper,
            nvals_combine_threshold,
            combiner,
            acc=None,
            reverse_sort=False,
    ) -> Matrix:
        self.force_combine_small_matrices(nvals_combine_threshold)

        for cur in sorted(
                (mapper(m) for m in self.matrices if m.nvals != 0),
                key=lambda m: m.nvals, reverse=reverse_sort
        ):
            acc = cur if acc is None else combiner(acc, cur)
        return mapper(self.base) if acc is None else acc

    def force_combine_small_matrices(self, nvals_combine_threshold):
        new_matrices = []
        for m in sorted(self.matrices, key=lambda m: m.nvals):
            if m.nvals <= nvals_combine_threshold and len(new_matrices) > 0:
                new_matrices[-1].iadd(m.to_unoptimized(), op=self.last_used_monoid)
            else:
                new_matrices.append(m)
        self.matrices = new_matrices

    def to_unoptimized(self) -> Matrix:
        self.force_combine_small_matrices(nvals_combine_threshold=float("inf"))
        return self.base.to_unoptimized()

    def mxm(self, other: Matrix, op: Semiring, swap_operands: bool = False) -> Matrix:
        self.update_monoid(op.monoid)
        return self._map_and_fold(
            mapper=lambda m: m.mxm(other, op=op, swap_operands=swap_operands),
            combiner=lambda acc, cur: acc.ewise_add(cur, op=op.monoid).new(),
            nvals_combine_threshold=other.nvals
        )

    def rsub(self, other, op: SubOp) -> Matrix:
        return self._map_and_fold(
            acc=other,
            reverse_sort=True,
            mapper=lambda m: m,
            combiner=lambda acc, cur: cur.rsub(acc, op),
            nvals_combine_threshold=other.nvals
        )

    def iadd(self, other: Matrix, op: Monoid):
        self.update_monoid(op)
        other = other.dup()
        if self.format is not None:
            other.ss.config["format"] = self.format
        base = self.base
        while True:
            other_nvals = max(other.nvals, self.min_size)
            i = next(
                (i for i in range(len(self.matrices))
                 if other_nvals / self.size_factor <=
                 max(self.min_size, self.matrices[i].nvals)
                 <= other_nvals * self.size_factor),
                None
            )

            if i is None:
                self.matrices.append(base.optimize_similarly(other))
                return self
            other << other.ewise_add(
                self.matrices[i].to_unoptimized(),
                op=op
            )
            del self.matrices[i]

    def update_monoid(self, op: Monoid):
        if self.last_used_monoid is not op:
            self.force_combine_small_matrices(nvals_combine_threshold=float("inf"))
            self.last_used_monoid = op

    def optimize_similarly(self, other: Matrix) -> OptimizedMatrix:
        return LazyAddOptimizedMatrix(
            self.base.optimize_similarly(other),
            nvals_factor=self.size_factor,
            min_nvals=self.min_size
        )

    def __sizeof__(self):
        return sum(m.__sizeof__() for m in self.matrices)
