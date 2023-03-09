from typing import List
from formula.formula import Formula
from formula.clause import Clause
from formula.variable import Variable
from pysat.formula import CNF as PySATCNF


class CNF(Formula):
    def __init__(self, clauses: List[Clause] = None) -> None:
        """Class representing conjunctive normal formula.

        Args:
            clauses (List[Clause], optional): Clauses within formula. Defaults to None.
        """
        self.clauses = clauses if clauses is not None else []
        self.max_var = 0
        for clause in self.clauses:
            for var in clause.variables:
                if var.id > self.max_var:
                    self.max_var = var.id

    @property
    def num_vars(self) -> int:
        """Number of variables in formula.

        Returns:
            int: Number of variables in formula. Assumes no gaps.
        """
        # Assumes formula has x_0 ... x_max_var
        return self.max_var + 1

    def append(self, clause: Clause) -> None:
        """Append clause to formula.

        Args:
            clause (Clause): Clause to append.
        """
        self.clauses.append(clause)
        # Check if clause contains variable not seen before.
        for var in clause.variables:
            if var.id > self.max_var:
                self.max_var = var.id

    def get_clause(self, index: int) -> Clause:
        """Get clause at index position in formula.

        Args:
            index (int): Index of clause, starts at 0.

        Returns:
            Clause: Clause at index postion in formula.
        """
        return self.clauses[index]

    def is_satisfied(self, assignment: str) -> bool:
        """Checks whether assignment provided satifies the formula.

        Args:
            assignment (str): Assignment, 1 corresponds to true and 0 to false.

        Returns:
            bool: True iff satisfied
        """
        if len(assignment) != self.num_vars:
            raise RuntimeError(
                f"Invalid assignment: expected length {self.num_vars}, actual length {len(assignment)}"
            )
        return all([c.is_satisfied(assignment) for c in self.clauses])

    def assignment_weight(self, assignment: str) -> float:
        """Weight of assignment (count of unsatisfied clauses in case of CNF).

        Args:
            assignment (str): Assignment of variables in clauses.

        Returns:
            float: Weight of assignment.
        """
        if len(assignment) != self.num_vars:
            raise RuntimeError(
                f"Invalid assignment: expected length {self.num_vars}, actual length {len(assignment)}"
            )
        return sum([not c.is_satisfied(assignment) for c in self.clauses])

    def to_pysat(self) -> PySATCNF:
        """Converts to PySat representation of CNF formula.

        Returns:
            PySATCNF: PySat representation of class.
        """
        pysatcnf = PySATCNF()
        for clause in self.clauses:
            pysatclause = []
            for var in clause.variables:
                # PySat starts numbering at 1
                pysatvar = var.id + 1
                if var.is_negation:
                    # Pysat uses negative to indicate negation
                    pysatvar = -1 * pysatvar
                pysatclause.append(pysatvar)
            pysatcnf.append(pysatclause)
        return pysatcnf

    def __repr__(self) -> str:
        return "∧\n".join([c.__str__() for c in self.clauses]) + "\n"

    def __str__(self) -> str:
        return "∧\n".join([c.__str__() for c in self.clauses]) + "\n"
