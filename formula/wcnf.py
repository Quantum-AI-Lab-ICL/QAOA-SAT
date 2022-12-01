from formula.cnf import CNF
from formula.clause import Clause
from typing import List, Tuple
from pysat.formula import WCNF as PySATWCNF


class WCNF(CNF):
    def __init__(self, clauses: List[Clause] = None, weights: List[float] = None) -> None:
        """Weighted CNF formula.

        Args:
            clauses (List[Clause], optional): Clauses of formula. Defaults to None.
            weights (List[float], optional): Weights of clauses. Defaults to all clause weights set to 1.
        """
        super().__init__(clauses)
        if weights is None and clauses is None:
            weights = [1 for _ in clauses]
        self.weights = weights

    @property
    def weighted_clauses(self) -> List[Tuple[Clause, float]]:
        return zip(self.clauses, self.weights)

    def append(self, clause: Clause, weight: float = 1) -> None:
        super().append(clause)
        self.weights.append(weight)

    def assignment_weight(self, assignment: str) -> float:
        return sum([w * c.is_satisfied(assignment) for (w, c) in self.weighted_clauses])

    def to_pysat(self) -> PySATWCNF:
        pysatcnf = super().to_pysat()
        pysatwcnf = pysatcnf.weighted()
        pysatwcnf.wght = self.weights
        return pysatwcnf
