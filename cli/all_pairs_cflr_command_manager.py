import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

import psutil

from src.grammar.cnf_grammar_template import CnfGrammarTemplate
from src.graph.label_decomposed_graph import LabelDecomposedGraph
from src.problems.Base.template_cfg.utils import explode_indices


def get_all_pairs_cflr_command_manager(
        algo_settings: str,
        graph_path: Path,
        grammar_path: Path
) -> "AllPairsCflrCommandManager":
    return {
        "pocr": PocrAllPairsCflrCommandManager,
        "pearl": PearlAllPairsCflrCommandManager,
        "gigascale": GigascaleAllPairsCflrCommandManager,
        "graspan": GraspanAllPairsCflrCommandManager
    }.get(algo_settings, PyAlgoAllPairsCflrCommandManager)(
        algo_settings, graph_path, grammar_path
    )


class AllPairsCflrCommandManager(ABC):
    def __init__(
            self,
            algo_settings: str,
            graph_path: Path,
            grammar_path: Path
    ):
        self.algo_settings = algo_settings
        self.graph_path = graph_path
        self.grammar_path = grammar_path

    @abstractmethod
    def create_command(self) -> str:
        pass

    # noinspection PyMethodMayBeStatic
    def discard_stderr(self) -> bool:
        return False

    @property
    def work_dir(self) -> Optional[Path]:
        return None

    # noinspection PyMethodMayBeStatic
    def get_analysis_time(self, output: str) -> float:
        return float(re.search(r"AnalysisTime\s+([\d.]+|NaN)", output).group(1))

    # noinspection PyMethodMayBeStatic
    def get_edge_count(self, output: str) -> int:
        return re.search(r"#(SEdges|CountEdges)\s+([\d.]+|NaN)", output).group(2)


class PyAlgoAllPairsCflrCommandManager(AllPairsCflrCommandManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_command(self) -> Optional[str]:
        return f"python3 -m cli.run_all_pairs_cflr {self.algo_settings} {self.graph_path} {self.grammar_path}"


class PocrAllPairsCflrCommandManager(AllPairsCflrCommandManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_command(self) -> Optional[str]:
        return (
            f'{self.grammar_path.stem} -pocr {self.graph_path}'
            if self.grammar_path.stem in {"aa", "vf"}
            else f'cfl -pocr {self.grammar_path} {self.graph_path}'
        )


class PearlAllPairsCflrCommandManager(AllPairsCflrCommandManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_command(self) -> Optional[str]:
        return (
            f'./{self.grammar_path.stem} {self.graph_path} -pearl -scc=false -gf=false'
            if self.grammar_path.stem in {"aa", "vf"}
            else None
        )

    @property
    def work_dir(self) -> Optional[Path]:
        return Path(os.environ['PEARL_DIR'])

    def get_edge_count(self, output: str) -> int:
        vedges_search = re.search(r"#VEdges\s+(\d+)", output)
        if vedges_search:
            return vedges_search.group(1)
        return re.search(r"#AEdges\s+(\d+)", output).group(1)


class GigascaleAllPairsCflrCommandManager(AllPairsCflrCommandManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_command(self) -> Optional[str]:
        return (
            f'./run.sh -wdlrb -i datasets/dacapo9/{self.graph_path.stem}'
            if self.grammar_path.stem in {"java_points_to"}
            else None
        )

    @property
    def work_dir(self) -> Optional[Path]:
        return Path(os.environ['GIGASCALE_DIR'])

    # Gigascale sends [INFO] logs to stderr
    def discard_stderr(self) -> bool:
        return True

    def get_analysis_time(self, output: str) -> float:
        return self._get_analysis_time_and_edge_count(output)[0]

    def get_edge_count(self, output: str) -> int:
        return self._get_analysis_time_and_edge_count(output)[1]

    @staticmethod
    def _get_analysis_time_and_edge_count(output: str) -> Tuple[float, int]:
        pattern = (r"benchmark\s+TC-time\s+TC-mem\s+v\s+e\s+vpt\s+avg\s+max\s+load/f\s+store/f\s*\n"
                   r"\w+\s+"
                   r"(\d+\.\d+)\s+"
                   r"\d+(?:\.\d+)?\s+"
                   r"\d+\s+"
                   r"\d+\s+"
                   r"(\d+)\s+"
                   r"\d+(?:\.\d+)?\s+"
                   r"\d+\s+"
                   r"\d+\s+"
                   r"\d+")

        match = re.search(pattern, output)

        tc_time, vpt = match.groups()
        return float(tc_time), int(vpt)


class GraspanAllPairsCflrCommandManager(AllPairsCflrCommandManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_command(self) -> Optional[str]:
        grammar = CnfGrammarTemplate.read_from_pocr_cnf_file(self.grammar_path)
        graph = LabelDecomposedGraph.read_from_pocr_graph_file(self.graph_path)

        # Graspan doesn't support indexed symbols, we need to concat labels and indices
        if graph.block_matrix_space.block_count > 1:
            graph, grammar = explode_indices(graph, grammar)
            graph_path = self.graph_path.parent / "graspan" / self.graph_path.name
            os.makedirs(graph_path.parent, exist_ok=True)
            graph.write_to_pocr_graph_file(graph_path)
        else:
            graph_path = self.graph_path

        # Graspan doesn't support grammars with over 255 symbols, because
        # each symbol is encoded with one byte and one symbol is reserved for epsilon
        if len(grammar.symbols) > 255:
            return None

        grammar_path = self.grammar_path.parent / "graspan" / self.grammar_path.name
        os.makedirs(grammar_path.parent, exist_ok=True)
        grammar.write_to_pocr_cnf_file(grammar_path, include_starting=False)

        return (
            f'./run {graph_path} {grammar_path} 1 '
            f'{int(psutil.virtual_memory().total / 10**9 * 0.9)} '
            f'{os.cpu_count() * 2}'
        )

    @property
    def work_dir(self) -> Optional[Path]:
        return Path(os.environ['GRASPAN_DIR']) / "src"

    def get_analysis_time(self, output: str) -> float:
        return float(re.search(r"COMP TIME:\s*([\d.]+|NaN)", output).group(1))

    def get_edge_count(self, output: str) -> int:
        final_file = re.search(r"finalFile:\s*(.*)", output).group(1)
        start_nonterm = CnfGrammarTemplate.read_from_pocr_cnf_file(self.grammar_path).start_nonterm
        with open(final_file, "r") as file:
            edges = set()
            for line in file:
                if line.split()[-1] == start_nonterm.label:
                    edges.add((line.split()[0], line.split()[1]))
        return len(edges)
