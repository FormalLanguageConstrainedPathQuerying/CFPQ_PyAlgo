class MCFG:
    def __init__(self, terminal_rules, nonterminal_rules, d_by_N, m):
        self.terminal_rules = terminal_rules
        self.nonterminal_rules = nonterminal_rules
        self.d_by_N = d_by_N
        self.m = m
        self.nonterminals = nonterminal_rules.keys()