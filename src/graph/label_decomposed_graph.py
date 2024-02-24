from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Union

import graphblas
import numpy as np
import pandas as pd
from graphblas import Matrix
from graphblas.core.dtypes import DataType, BOOL
from graphblas.core.operator import Monoid, Semiring
from graphblas.exceptions import IndexOutOfBound

from src.grammar.cnf_grammar_template import CnfGrammarTemplate, Symbol
from src.matrix.block.block_matrix_space import BlockMatrixSpace
from src.matrix.block.block_matrix_space_impl import BlockMatrixSpaceImpl
from src.matrix.matrix_optimizer_setting import MatrixOptimizerSetting, optimize_matrix
from src.matrix.optimized_matrix import OptimizedMatrix
from src.utils.subtractable_semiring import SubOp


class LabelDecomposedGraph:
    """
    Representation of an edge labeled graph where labels are of type `(Symbol, Optional[int])`,
    i.e. each label is represented by a combination of "label symbol" and an optional "label index".
    
    For each label string an adjacency matrix is stored.
    
    If "label symbol" is used without indices, then its adjacency
    matrix is a square matrix of shape `(vertex_count, vertex_count)`.
    
    If "label symbol" is used with indices, then its adjacency matrix is a
    block-matrix of shape `(block_matrix_space.block_count * vertex_count, vertex_count)`
    or `(vertex_count, block_matrix_space.block_count * vertex_count)`, where
    `block_matrix_space.block_count` is the largest "label index" in the entire graph.
    """
    def __init__(
        self,
        vertex_count: int,
        block_matrix_space: BlockMatrixSpace,
        dtype: DataType,
        matrices: Dict[Symbol, Matrix],
    ):
        self.vertex_count = vertex_count
        self.block_matrix_space = block_matrix_space
        self.dtype = dtype
        self.matrices = matrices

    @property
    def nvals(self) -> int:
        return sum(m.nvals for m in self.matrices.values())

    @staticmethod
    def read_from_pocr_graph_file(path: Union[Path, str]) -> "LabelDecomposedGraph":
        try:
            dfs = pd.read_csv(
                path,
                delim_whitespace=True,
                header=None,
                names=['EDGE_SOURCE', 'EDGE_DESTINATION', 'EDGE_LABEL', 'LABEL_INDEX'],
                dtype={'EDGE_SOURCE': np.int64, 'EDGE_DESTINATION': np.int64, 'EDGE_LABEL': str,
                       'LABEL_INDEX': pd.Int64Dtype()},
                chunksize=1_000_000
            )

            # edge_label -> (edge_source_chunks, edge_destination_chunks, label_index_chunks)
            data_chunks = defaultdict(lambda: ([], [], []))

            for df in dfs:
                df['LABEL_INDEX'].fillna(0, inplace=True)

                for label, group in df.groupby('EDGE_LABEL'):
                    symbol = Symbol(label)
                    data_chunks[symbol][0].append(group['EDGE_SOURCE'].to_numpy(dtype=np.int64))
                    data_chunks[symbol][1].append(group['EDGE_DESTINATION'].to_numpy(dtype=np.int64))
                    data_chunks[symbol][2].append(group['LABEL_INDEX'].to_numpy(dtype=np.int64))

            vertex_count = 1
            block_count = 1

            # edge_label -> (edge_sources, edge_destinations, label_indices)
            data = dict()

            for symbol, (edge_source_chunks, edge_destination_chunks, label_index_chunks) in data_chunks.items():
                edge_sources = np.concatenate(edge_source_chunks)
                edge_destinations = np.concatenate(edge_destination_chunks)
                label_indices = np.concatenate(label_index_chunks)

                data[symbol] = (edge_sources, edge_destinations, label_indices)

                vertex_count = max(vertex_count, int(edge_sources.max()) + 1, int(edge_destinations.max()) + 1)
                block_count = max(block_count, int(label_indices.max()) + 1)

            matrices: Dict[Symbol, Matrix] = dict()
            for symbol, (edge_sources, edge_destinations, label_indices) in data.items():
                edge_sources += label_indices * vertex_count

                try:
                    matrices[symbol] = Matrix.from_coo(
                        rows=edge_sources,
                        columns=edge_destinations,
                        values=True,
                        nrows=block_count * vertex_count if symbol.is_indexed else vertex_count,
                        ncols=vertex_count
                    )
                except IndexOutOfBound as e:
                    raise ValueError(
                        f"Failed to create adjacency matrix for label '{symbol.label}'.\n"
                        f"This issue is usually caused by using indexes for label without '_i' suffix.\n"
                        f"Consider adding suffix '_i' to label '{symbol.label}'."
                    ) from e

            return LabelDecomposedGraph(
                vertex_count=vertex_count,
                block_matrix_space=BlockMatrixSpaceImpl(n=vertex_count, block_count=block_count),
                dtype=BOOL,
                matrices=matrices
            )
        except Exception as e:
            raise ValueError(
                f"Invalid graph file '{path}'. All lines of graph file should have form:\n"
                "```\n"
                "<EDGE_SOURCE>\t<EDGE_DESTINATION>\t<EDGE_LABEL>\t[LABEL_INDEX]\n"
                "```\n"
                "Whitespace characters should be used to separate values on one line.\n"
                "[LABEL_INDEX] is optional.\n"
                "Indexed labels names must end with '_i'."
            ) from e

    def __sizeof__(self) -> int:
        return sum(m.__sizeof__() for m in self.matrices.values())


class OptimizedLabelDecomposedGraph:
    """
    Representation of an edge labeled graph similar to `LabelDecomposedGraph`,
    but with `OptimizedMatrix` instead of regular `Matrix`.
    """
    def __init__(
        self,
        vertex_count: int,
        block_matrix_space: BlockMatrixSpace,
        dtype: DataType,
        matrix_optimizers: List[MatrixOptimizerSetting]
    ):
        self.vertex_count = vertex_count
        self.block_matrix_space = block_matrix_space
        self.dtype = dtype
        self.matrix_optimizers = matrix_optimizers
        self.matrices: Dict[Symbol, OptimizedMatrix] = dict()

    @staticmethod
    def from_unoptimized(
        unoptimized_graph: LabelDecomposedGraph,
        matrix_optimizers: List[MatrixOptimizerSetting]
    ) -> "OptimizedLabelDecomposedGraph":
        optimized_graph = OptimizedLabelDecomposedGraph(
            vertex_count=unoptimized_graph.vertex_count,
            block_matrix_space=unoptimized_graph.block_matrix_space,
            dtype=unoptimized_graph.dtype,
            matrix_optimizers=matrix_optimizers
        )
        optimized_graph.iadd(unoptimized_graph, op=graphblas.monoid.any)
        return optimized_graph

    def empty_copy(self) -> "OptimizedLabelDecomposedGraph":
        return OptimizedLabelDecomposedGraph(
            vertex_count=self.vertex_count,
            block_matrix_space=self.block_matrix_space,
            matrix_optimizers=self.matrix_optimizers,
            dtype=self.dtype,
        )

    def to_unoptimized(self) -> LabelDecomposedGraph:
        return LabelDecomposedGraph(
            vertex_count=self.vertex_count,
            block_matrix_space=self.block_matrix_space,
            matrices={
                symbol: matrix.to_unoptimized()
                for symbol, matrix in self.matrices.items()
            },
            dtype=self.dtype,
        )

    @property
    def nvals(self) -> int:
        return sum(matrix.nvals for matrix in self.matrices.values())

    def iadd_by_symbol(self, symbol: Symbol, matrix: Matrix, op: Monoid):
        if symbol not in self:
            self.matrices[symbol] = self.block_matrix_space.automize_block_operations(
                optimize_matrix(self._create_matrix_for_symbol(symbol), self.matrix_optimizers)
            )
        self.matrices[symbol].iadd(matrix, op)

    def iadd(self, other: LabelDecomposedGraph, op: Monoid):
        for symbol, matrix in other.matrices.items():
            self.iadd_by_symbol(symbol, matrix, op)
        return self

    def rsub(self, other: LabelDecomposedGraph, op: SubOp) -> LabelDecomposedGraph:
        return LabelDecomposedGraph(
            vertex_count=self.vertex_count,
            block_matrix_space=self.block_matrix_space,
            dtype=self.dtype,
            matrices={
                symbol: (self.matrices[symbol].rsub(matrix, op) if symbol in self else matrix)
                for symbol, matrix in other.matrices.items()
            },
        )

    def mxm(
            self,
            other: LabelDecomposedGraph,
            grammar: CnfGrammarTemplate,
            op: Semiring,
            accum: Optional["OptimizedLabelDecomposedGraph"] = None,
            swap_operands: bool = False,
    ) -> "OptimizedLabelDecomposedGraph":
        if accum is None:
            accum = self.empty_copy()
        for (lhs, rhs1, rhs2) in grammar.complex_rules:
            if swap_operands:
                rhs1, rhs2 = rhs2, rhs1
            if rhs1 in self.matrices and rhs2 in other.matrices:
                mxm = self.matrices[rhs1].mxm(
                    other.matrices[rhs2],
                    swap_operands=swap_operands,
                    op=op,
                )
                accum.iadd_by_symbol(lhs, mxm, op.monoid)
        return accum

    def rmxm(
            self,
            other: LabelDecomposedGraph,
            grammar: CnfGrammarTemplate,
            op: Semiring,
            accum: Optional["OptimizedLabelDecomposedGraph"] = None
    ) -> "OptimizedLabelDecomposedGraph":
        return self.mxm(other, grammar, op, accum, swap_operands=True)

    def __getitem__(self, symbol: Symbol) -> Matrix:
        return (
            self.matrices[symbol].to_unoptimized()
            if symbol in self
            else self._create_matrix_for_symbol(symbol)
        )

    def _create_matrix_for_symbol(self, symbol):
        return self.block_matrix_space.create_space_element(self.dtype, is_vector=symbol.is_indexed)

    def __contains__(self, symbol: Symbol) -> bool:
        return symbol in self.matrices

    def __sizeof__(self) -> int:
        return sum(m.__sizeof__() for m in self.matrices.values())
