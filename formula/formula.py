from abc import ABC, abstractmethod, abstractproperty
from typing import Iterable, List
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

    @abstractproperty
    def naive_sats(self) -> Iterable[int]:
        """Finds all satisfying bitstrings. Use singleton pattern to only evaluate once.

        Returns:
            Iterable[int]: Value at index 1 iff bitstring satisfies, in bistring order.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )

    @abstractproperty
    def naive_counts(self) -> Iterable[int]:
        """Finds number of unsatisfied clauses for all bitstrings. Use singleton pattern to only evaluate once.

        Returns:
            Iterable[int]: Number of unsatisfied clauses in bistring order.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )
