import numpy as np
from typing import Iterable, List

from formula.clause import Clause
from formula.cnf import CNF


class NAECNF(CNF):
    def __init__(self, clauses: List[Clause] = None) -> None:
        super().__init__(clauses)

    def is_satisfied(self, assignment: str) -> bool:
        """Checks whether assignment provided satisfies the formula in NAE formulation.

        Args:
			assignment (str): Assignment, 1 corresponds to true and 0 to false.

        Returns:
			bool: True iff every clause satisfied but literals not same to truth value.
        """
        if len(assignment) != self.num_vars:
            raise RuntimeError(
                f"Invalid assignment: expected length {self.num_vars}, actual length {len(assignment)}"
            )
        return all(
            [
                c.is_satisfied(assignment) and not c.all_same(assignment)
                for c in self.clauses
            ]
        )

    def assignment_weight(self, assignment: str) -> float:
        """Count of unsatisfied clauses.

        Args:
			assignment (str): Assignment of variables in clauses.

        Returns:
			float: Weight of assignment.
        """
        if len(assignment) != self.num_vars:
            raise RuntimeError(
                f"Invalid assignment: expected length {self.num_vars}, actual length {len(assignment)}"
            )
        return sum(
            [
                not c.is_satisfied(assignment) or c.all_same(assignment)
                for c in self.clauses
            ]
        )
