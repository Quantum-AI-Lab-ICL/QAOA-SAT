from abc import ABC, abstractmethod, abstractproperty
from typing import List
from formula.clause import Clause


class Formula(ABC):
    @abstractmethod
    def __init__(self, clauses: List[Clause] = None) -> None:
        """Class representing Boolean formula.

        Args:
            clauses (List[Clause], optional): Clauses of formula. Defaults to no clauses.

        Raises:
            NotImplementedError: Attempted initialisation of abstract base formula class.
        """
        raise NotImplementedError(
            "Attempted initialisation of abstract base formula class"
        )

    @abstractproperty
    def num_vars(self) -> int:
        """Number of variables in formula.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class property.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class property"
        )

    @abstractmethod
    def is_satisfied(self, assignment: str) -> bool:
        """Determines if clauses of formula are satisfied by assignment.

        Args:
            assignment (str): Assignment for variables in clauses.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )
    
    @abstractmethod
    def assignment_weight(self, assignment: str) -> float:
        """Weight of assignment.

        Args:
            assignment (str): Assignment of variables in clauses.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )
        