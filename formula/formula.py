from abc import ABC, abstractmethod
from typing import List
from formula.clause import Clause


class Formula(ABC):
    @abstractmethod
    def __init__(self, clauses: List[Clause] = None) -> None:
        """Class representing Boolean formula.

        Args:
            clauses (List[Clause], optional): Clauses of formula. Defaults to no clauses.

        Raises:
            NotImplementedError: Attempted initialisation of abstract base formula class
        """
        raise NotImplementedError(
            "Attempted initialisation of abstract base formula class"
        )

    @abstractmethod
    def is_satisfied(self, assignment: str) -> bool:
        """Determines if clauses of formula are satisfied by assignment.

        Args:
            assignment (str): Assignment for variables in clauses.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method

        Returns:
            bool: True iff all clauses are satisfied
        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )
