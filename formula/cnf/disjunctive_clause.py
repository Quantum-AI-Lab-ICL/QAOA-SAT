from typing import List
from formula.clause import Clause
from formula.variable import Variable
from functools import reduce
from itertools import combinations


class DisjunctiveClause(Clause):
    def __init__(self, variables: List[Variable] = None) -> None:
        """Class representing a disjunctive clause within a Boolean formula.

        Args:
            variables (List[Variable], optional): Variables within clause. Defaults to None.
        """
        self.variables = variables if variables is not None else []

        # Remove duplicates
        self.variables = list(dict.fromkeys(self.variables))

        # Check for LEM
        self.always_sat = any(
            [v1.id == v2.id for (v1, v2) in combinations(self.variables, r=2)]
        )

    @property
    def variables(self) -> List[Variable]:
        """Variables in clause.

        Returns:
            List[Variable]: Variables in clause.
        """
        return self.variables

    @property
    def num_vars(self) -> int:
        """Number of variables in clause.

        Returns:
            int: Number of variables in clause.
        """
        return len(self.variables)

    def append(self, variable: Variable) -> None:
        """Add variable to end of clause.

        Args:
            variable (Variable): Variable to add to end of clause.
        """
        # Check variable isn't already in clause
        if not variable in self.variables:
            self.variables.append(variable)

        # Check for LEM
        self.always_sat = any(
            [v1.id == v2.id for (v1, v2) in combinations(self.variables, r=2)]
        )

    def get_variable(self, index: int) -> Variable:
        """Get variable at index position in clause.

        Args:
            index (int): Position of variable to retrieve. Starts at 0.

        Returns:
            Variable: Variable at index position in clause.
        """
        return self.variables[index]

    def is_satisfied(self, assignment: str) -> bool:
        """Determines whether clause is satisfied by assignment.

        Args:
            assignment (str): Assignment for variables.

        Returns:
            bool: True iff clause is satisfied
        """
        return self.always_sat or any(
            [v.is_satisfied(assignment) for v in self.variables]
        )

    def all_same(self, assignment: str) -> bool:
        """Determines whether literals in clause all set to same truth value.

        Args:
            assignment (str): Assignment for variables.

        Returns:
            bool: True iff all literals set to same truth value.
        """
        return all([v.is_satisfied(assignment) for v in self.variables])

    def parity(self, vars: List[Variable] = None) -> int:
        """Parity of clause (as defined in notebook.)

        Args:
            vars (List[Variable], optional): Subset of clause to consider. Defaults to entire clause.

        Returns:
            int: Parity of (subset of) clause
        """
        if vars is None:
            vars = self.variables
        r = reduce(lambda x, y: x ^ y, [not v.is_negation for v in vars], False)
        return -1 if r else 1

    def __repr__(self) -> str:
        return "(" + " ∨ ".join([v.__str__() for v in self.variables]) + ")"

    def __str__(self) -> str:
        return "(" + " ∨ ".join([v.__str__() for v in self.variables]) + ")"
