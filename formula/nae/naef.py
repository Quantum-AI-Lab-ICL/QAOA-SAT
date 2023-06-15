from typing import List
from pysat.formula import CNF as PySATCNF

from formula.cnf.cnf import CNF
from formula.nae.nae_clause import NAEClause
from formula.variable import Variable


class NAEFormula(CNF):
    def __init__(self, clauses: List[NAEClause] = None) -> None:
        """Class representing NAE formula (extension of CNF).

        Args:
            clauses (List[NAEClause], optional): Clauses within formula. Defaults to None.
        """
        assert clauses is None or all([isinstance(c, NAEClause) for c in clauses])
        super().__init__(clauses)

    def append(self, clause: NAEClause) -> None:
        """Append clause to formula.

        Args:
            clause (Clause): Clause to append.
        """
        assert isinstance(clause, NAEClause)
        super().append(clause)

    @classmethod
    def from_pysat(cls, formula: PySATCNF) -> None:
        """Creates formula from pysat formula.

        Args:
            formula (PySATFormula): Pysat formula to use.
        """

        clauses = []
        for clause in formula.clauses:
            c = NAEClause()
            for var in clause:
                # PySat starts numbering at 1 and uses negative to indicate negation
                v = Variable(abs(var) - 1, is_negation=var < 0)
                c.append(v)
            clauses.append(c)
        return cls(clauses)

    @classmethod
    def from_file(cls, filename: str) -> None:
        """Creates formula from CNF file.

        Args:
            filename (str): File to read from.
        """

        # Use PySAT as interface
        pcnf = PySATCNF(from_file=filename)
        return NAEFormula.from_pysat(pcnf)