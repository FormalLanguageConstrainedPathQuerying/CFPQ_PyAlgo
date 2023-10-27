from dataclasses import dataclass
from typing import List, Tuple, Iterable

from src.grammar.cnf_grammar import CnfGrammar


@dataclass
class HyperSimpleRule:
    nonterm: str
    term_prefix: str
    term_suffix: str


class HyperCnfGrammar:
    def __init__(
        self,
        start_nonterm: str,
        hyper_nonterms: List[str],
        hyper_simple_rules: List[HyperSimpleRule],
        simple_rules: List[Tuple[str, str]],
        complex_rules: List[Tuple[str, str, str]],
        eps_rules: List[str]
    ):
        self.start_nonterm = start_nonterm
        self.hyper_nonterms = hyper_nonterms
        self.hyper_simple_rules = hyper_simple_rules
        self.simple_rules = simple_rules
        self.complex_rules = complex_rules
        self.eps_rules = eps_rules

    @staticmethod
    def from_cnf(cnf_grammar: CnfGrammar):
        return HyperCnfGrammar(
            start_nonterm=cnf_grammar.start_nonterm,
            hyper_nonterms=[],
            hyper_simple_rules=[],
            simple_rules=cnf_grammar.simple_rules,
            complex_rules=cnf_grammar.complex_rules,
            eps_rules=cnf_grammar.eps_rules
        )

    def get_hyper_nonterm_size(self, terms: Iterable[str]) -> int:
        hyper_term_max_idx = 0
        for rule in self.hyper_simple_rules:
            for term in terms:
                if term.startswith(rule.term_prefix) and term.endswith(rule.term_suffix):
                    trimmed_term = (
                        term[len(rule.term_prefix):-len(rule.term_suffix)]
                        if len(rule.term_suffix) > 0
                        else term[len(rule.term_prefix):]
                    )
                    if trimmed_term.isdigit():
                        hyper_term_max_idx = max(hyper_term_max_idx, int(trimmed_term))
        return hyper_term_max_idx + 1

    @staticmethod
    def from_hcnf(path: str) -> "HyperCnfGrammar":
        cnf = CnfGrammar.from_cnf(path)
        return HyperCnfGrammar(
            start_nonterm=cnf.start_nonterm,
            hyper_nonterms=[nonterm for nonterm in cnf.nonterms if HyperCnfGrammar._is_hyper_name(nonterm)],
            hyper_simple_rules=[
                HyperSimpleRule(l, *HyperCnfGrammar._split_hyper_name(r))
                for (l, r) in cnf.simple_rules
                if HyperCnfGrammar._is_hyper_name(r)
            ],
            simple_rules=[(l, r) for (l, r) in cnf.simple_rules if not HyperCnfGrammar._is_hyper_name(r)],
            complex_rules=cnf.complex_rules,
            eps_rules=cnf.eps_rules
        )

    @staticmethod
    def _is_hyper_name(name: str):
        return name.endswith("_i") or "_i_" in name

    @staticmethod
    def _split_hyper_name(name: str) -> Tuple[str, str]:
        if name.endswith("_i"):
            return (name[:-len("_i")] + "_"), ""
        prefix, suffix = name.split("_i_")
        return (prefix + "_"), ("_" + suffix)
