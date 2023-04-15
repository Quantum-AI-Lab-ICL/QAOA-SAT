from abc import ABC, abstractmethod, abstractproperty, abstractstaticmethod
from typing import Iterable, List, Union
from pysat.formula import CNF as PySATCNF
from pysat.formula import WCNF as PySATWCNF

from formula.clause import Clause

PySATFormula = Union[PySATCNF, PySATWCNF]

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

    @abstractmethod
    def to_pysat(self) -> PySATFormula:
        """Converts to PySat representation of formula.

        Returns:
            PySATFormula: PySat representation of class.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )
    
    @classmethod
    @abstractmethod
    def from_pysat(cls, formula: PySATFormula) -> None:
        """Creates formula from pysat formula.

        Args:
            formula (PySATFormula): Pysat formula to use.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )

    @abstractmethod
    def to_file(self, filename: str) -> None:
        """Converts to CNF file representation of formula.

        Args:
            filename (str): File to write to.

        Raises:
            NotImplementedError: Attempted invocation of abstract base formula class method.

        """
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )
    
    @classmethod
    @abstractmethod
    def from_file(cls, filename: str) -> None:
        """Creates formula from CNF file.

        Args:
            filename (str): File to read from.

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