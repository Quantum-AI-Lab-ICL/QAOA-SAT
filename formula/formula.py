from abc import ABC, abstractmethod, abstractproperty
from typing import Iterable, List

from formula.clause import Clause


class Formula(ABC):
    @abstractmethod
    def __init__(self, clauses: List[Clause] = None) -> None:
        """Class representing Boolean formula.

        Args:
            clauses (List[Clause], optional): Clauses of formula. Defaults to no clauses.
        """
        pass

    @abstractproperty
    def num_vars(self) -> int:
        """Number of variables in formula.

        Returns:
            int: Number of variables in formula.
        """
        pass

    @abstractmethod
    def is_satisfied(self, assignment: str) -> bool:
        """Determines if formula is satisfied by assignment.

        Args:
            assignment (str): Assignment for variables in clauses.

        Returns:
            bool: True iff formula satisfied by assignment.
        """
        pass

    @abstractmethod
    def assignment_weight(self, assignment: str) -> float:
        """Weight of assignment (unsatisfied clauses).

        Args:
            assignment (str): Assignment of variables in clauses.

        Returns:
            float: Assignment weight.
        """
        pass

    @abstractmethod
    def unsatisfied_clauses(self, assignment: str) -> List[Clause]:
        """Find clauses unsatisfied by assignment.

        Args:
            assignment (str): Assignment of variables in clauses.

        Returns:
            List[Clause]: _description_
        """
        pass

    @abstractproperty
    def naive_sats(self) -> Iterable[int]:
        """Finds all satisfying bitstrings. Use singleton pattern to only evaluate once.

        Returns:
            Iterable[int]: Value at index 1 iff bitstring satisfies, in bistring order.
        """
        pass

    @abstractmethod
    def random_assignment(self) -> str:
        """Make a random assignment to formula.

        Returns:
            str: Bitstring corresponding to assignment.
        """
        pass
