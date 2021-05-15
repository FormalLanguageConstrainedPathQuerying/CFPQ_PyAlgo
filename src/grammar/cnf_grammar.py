class CnfGrammar:
    """
    This class representing grammar in CNF
    """
    def __init__(self):
        self.start_nonterm = None
        self.nonterms = set()
        self.terms = set()
        self.simple_rules = []
        self.complex_rules = []

    def __setitem__(self, key, value):
        if (isinstance(value, tuple) or isinstance(value, list)) and 1 <= len(value) <= 2:
            self.nonterms.add(key)
            if len(value) == 1:
                self.simple_rules.append((key, value[0]))
                self.terms.add(value[0])
            else:
                self.complex_rules.append((key, value[0], value[1]))
                for x in value:
                    self.nonterms.add(x)
        else:
            raise Exception('value must be str, (str, str) or [str, str]')

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
