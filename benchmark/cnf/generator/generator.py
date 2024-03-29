from abc import ABC, abstractmethod
from typing import List
from formula.cnf.disjunctive_clause import DisjunctiveClause

from formula.variable import Variable
from formula.cnf.cnf import CNF


class Generator(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """Generator for random problems."""
        pass

    @abstractmethod
    def from_file(
        self, n: int, k: int, calc_naive: bool = False, index: int = 0
    ) -> CNF:
        """ Get problem from file.

            Args:
                n (int): Number of variables per instance.
                k (int): Variables per clause per instance.
                calc_naive (bool, optional): Read in unsat counts. Defaults to False.
                index (int, optional): File index. Defaults to 0.

            Returns:
                CNF: Problem instance.
        """
        pass

    @abstractmethod
    def filename(self, n: int, k: int, index: int = 0, suffix: str = "cnf") -> str:
        """ Get filename corresponding to problem.

            Args:
                n (int): Number of variables per instance.
                k (int): Variables per clause per instance.
                index (int, optional): File index. Defaults to 0.
                suffix (int, optional): File suffix. Defaults to cnf.

            Returns:
                str: Filename corresponding to CNF problem.

        """
        pass

    @abstractmethod
    def directory(self, n: int, k: int) -> str:
        """ Get directory corresponding to problem type.

            Args:
                n (int): Number of variables per instance.
                k (int): Variables per clause per instance.

            Returns:
                str: Filename corresponding to CNF type.
        """
        pass

    @abstractmethod
    def variables_from_count(self, c: int) -> List[Variable]:
        """ Generate $\{x_0, ~x_0, ... x_{c-1}, ~x_{c-1}\}$

            Args:
                count (int): Id to generate up to.

            Returns:
                List[Variable]: $\{x_0, ~x_0, ... x_{c-1}, ~x_{c-1}\}$
        """
        pass

    @abstractmethod
    def is_satisfiable(self, f: CNF) -> bool:
        """ Verify if formula is satisfiable.

            Args:
                f (CNF): CNF to check satisfiability of.

            Returns:
                bool: Boolean variable set to true iff formula is satisfiable.
        """
        pass

    @abstractmethod
    def ratio(self, k: int) -> float:
        """ Satisfiability ratio for k-SAT problem.

            Args:
                k (int): Variables per clause.

            Returns:
                float: Satisfiability ratio for value of k.
        """
        pass

    @abstractmethod
    def empty_formula(self) -> CNF:
        """ Empty formula.

            Returns:
                CNF: Empty formula.
        """
        pass

    @abstractmethod
    def empty_clause(self) -> DisjunctiveClause:
        """ Empty Clause.

            Returns:
                DisjunctiveClause: Empty clause.
        """
        pass
