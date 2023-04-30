from typing import List

from formula.cnf import CNF
from formula.nae.nae_clause import NAEClause


class NAEFormula(CNF):
    def __init__(self, clauses: List[NAEClause] = None) -> None:
        """Class representing NAE formula (extension of CNF).

        Args:
            clauses (List[NAEClause], optional): Clauses within formula. Defaults to None.
        """
        assert all([isinstance(c, NAEClause) for c in clauses])
        super().__init__(clauses)

    def append(self, clause: NAEClause) -> None:
        """Append clause to formula.

        Args:
            clause (Clause): Clause to append.
        """
        assert isinstance(clause, NAEClause)
        super().append(clause)