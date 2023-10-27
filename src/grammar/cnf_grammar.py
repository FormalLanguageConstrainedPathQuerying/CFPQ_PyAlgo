from cfpq_data import cnf_from_cfg
from pyformlang.cfg import CFG


class CnfGrammar:
    """
    This class representing grammar in CNF. Supports only the functions necessary for the algorithms to work
    """

    def __init__(self):
        self.start_nonterm = None
        self.nonterms = set()
        self.terms = set()
        self.simple_rules = []
        self.complex_rules = []
        self.eps_rules = []

    def __setitem__(self, key, value):
        if (isinstance(value, tuple) or isinstance(value, list)) and 0 <= len(value) <= 2:
            self.nonterms.add(key)
            if len(value) == 0:
                self.eps_rules.append(key)
            elif len(value) == 1:
                self.simple_rules.append((key, value[0]))
                self.terms.add(value[0])
            else:
                self.complex_rules.append((key, value[0], value[1]))
                for x in value:
                    self.nonterms.add(x)
        else:
            raise Exception('value must be str, (str, str) or [str, str]')

    @classmethod
    def from_cfg(cls, cfg: CFG):
        cnf = CnfGrammar()
        base_cnf = cnf_from_cfg(cfg)
        cnf.start_nonterm = base_cnf.start_symbol.to_text()

        for product in base_cnf.productions:
            if not product.body:
                cnf.eps_rules.append(product.head.to_text().strip('"'))
            else:
                cnf[product.head.to_text().strip('"')] = [x.to_text().strip('"') for x in product.body]

        return cnf

    @classmethod
    def from_cnf(cls, path):
        """
        Load grammar in CNF format from file
        @param path: path to file with grammar
        @return: initialized class
        """
        grammar = CnfGrammar()
        with open(path, 'r') as f:
            lines = f.readlines()
            grammar.start_nonterm = lines[0].split()[0].strip()
            for line in lines[2:]:
                l, r = line.strip().split('->')
                l = l.strip()
                r = r.strip().split()
                grammar[l] = r
        return grammar
