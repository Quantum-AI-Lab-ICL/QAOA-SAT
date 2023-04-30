from typing import Iterable, List
import pathos
import os
import numpy as np
import random
from formula.clause import Clause

from formula.formula import Formula
from formula.cnf.disjunctive_clause import DisjunctiveClause
from formula.variable import Variable
from pysat.formula import CNF as PySATCNF


class CNF(Formula):
    def __init__(self, clauses: List[DisjunctiveClause] = None) -> None:
        """Class representing conjunctive normal formula.

        Args:
            clauses (List[DisjunctiveClause], optional): Clauses within formula. Defaults to None.
        """
        self.clauses = clauses if clauses is not None else []
        self.max_var = 0
        for clause in self.clauses:
            for var in clause.variables:
                if var.id > self.max_var:
                    self.max_var = var.id

        self.counts = None
        self.sats = None

    @classmethod
    def from_pysat(cls, formula: PySATCNF) -> None:
        """Creates formula from pysat formula.

        Args:
            formula (PySATFormula): Pysat formula to use.
        """

        clauses = []
        for clause in formula.clauses:
            c = DisjunctiveClause()
            for var in clause:
                # PySat starts numbering at 1 and uses negative to indicate negation
                v = Variable(abs(var) - 1, is_negation=var < 0)
                c.append(v)
            clauses.append(c)
        return cls(clauses)

    @classmethod
    def from_file(cls, filename: str) -> None:
        """Creates formula from CNF file.

        Args:
            filename (str): File to read from.
        """

        # Use PySAT as interface
        pcnf = PySATCNF(from_file=filename)
        return CNF.from_pysat(pcnf)

    @property
    def num_vars(self) -> int:
        """Number of variables in formula.

        Returns:
            int: Number of variables in formula. Assumes no gaps.
        """
        # Assumes formula has x_0 ... x_max_var
        return self.max_var + 1

    def append(self, clause: DisjunctiveClause) -> None:
        """Append clause to formula.

        Args:
            clause (DisjunctiveClause): Clause to append.
        """
        self.clauses.append(clause)
        # Check if clause contains variable not seen before.
        for var in clause.variables:
            if var.id > self.max_var:
                self.max_var = var.id

    def get_clause(self, index: int) -> DisjunctiveClause:
        """Get clause at index position in formula.

        Args:
            index (int): Index of clause, starts at 0.

        Returns:
            DisjunctiveClause: Clause at index postion in formula.
        """
        return self.clauses[index]

    def is_satisfied(self, assignment: str) -> bool:
        """Checks whether assignment provided satisfies the formula.

        Args:
            assignment (str): Assignment, 1 corresponds to true and 0 to false.

        Returns:
            bool: True iff satisfied
        """
        if len(assignment) != self.num_vars:
            raise RuntimeError(
                f"Invalid assignment: expected length {self.num_vars}, actual length {len(assignment)}"
            )
        # Could call assignment weight == 0 but 'all' allows for lazy evaluation
        return all([c.is_satisfied(assignment) for c in self.clauses])

    def assignment_weight(self, assignment: str) -> float:
        """Weight of assignment (unsatisfied clauses).

        Args:
            assignment (str): Assignment of variables in clauses.

        Returns:
            float: Weight of assignment.
        """
        if len(assignment) != self.num_vars:
            raise RuntimeError(
                f"Invalid assignment: expected length {self.num_vars}, actual length {len(assignment)}"
            )
        return len(self.unsatisfied_clauses(assignment))

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

    def to_file(self, filename: str) -> None:
        """Converts to CNF file representation of formula.

        Args:
            filename (str): File to write to.
        """

        # Use PySAT as interface
        pcnf = self.to_pysat()
        pcnf.to_file(filename)

    @property
    def naive_sats(self) -> Iterable[int]:
        """Finds all satisfying bitstrings. Use singleton pattern to only evaluate once.

        Returns:
            Iterable[int]: Value at index 1 iff bitstring satisfies, in bistring order.

        """
        if self.sats is None:
            naive_counts = self.naive_counts
            self.sats = np.where(naive_counts == 0.0)[0]
        return self.sats

    @property
    def naive_counts(self) -> Iterable[int]:
        """Finds number of unsatisfied clauses for all bitstrings. Use singleton pattern to only evaluate once.

        Returns:
            Iterable[int]: Number of unsatisfied clauses in bistring order.
        """
        if self.counts is None:
            n = self.num_vars
            N = 2**n
            bs = [bin(i)[2:].zfill(n) for i in range(N)]
            with pathos.multiprocessing.Pool(os.cpu_count() - 1) as executor:
                counts = list(executor.map(self.assignment_weight, bs))
                self.counts = np.array(counts, dtype=np.float32)
        return self.counts

    def random_assignment(self) -> str:
        """Make a random assignment to formula.

        Returns:
            str: Bitstring corresponding to assignment.

        """
        return ''.join(random.choice(['0', '1']) for _ in range(self.num_vars)) 

    def unsatisfied_clauses(self, assignment: str) -> List[Clause]:
        """Find clauses unsatisfied by assignment.

        Args:
            assignment (str): Assignment of variables in clauses.

        Returns:
            List[Clause]: _description_
        """
        return [clause for clause in self.clauses if not clause.is_satisfied(assignment)] 

    def __repr__(self) -> str:
        return "∧\n".join([c.__str__() for c in self.clauses]) + "\n"

    def __str__(self) -> str:
        return "∧\n".join([c.__str__() for c in self.clauses]) + "\n"
