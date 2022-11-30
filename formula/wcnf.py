from formula.cnf import CNF
from formula.clause import Clause
from typing import List, Tuple
from pysat.formula import WCNF as PySATWCNF


class WCNF(CNF):
    def __init__(self, clauses: List[Clause], weights: List[float]) -> None:
        super().__init__(clauses)
        self.weights = weights

    @property
    def weighted_clauses(self) -> List[Tuple[Clause, float]]:
        return zip(self.clauses, self.weights)

    def assignment_weight(self, assignment: str) -> float:
        return sum([w * c.is_satisfied(assignment) for (w, c) in self.weighted_clauses])

    def to_pysat(self) -> PySATWCNF:
        pysatcnf = super().to_pysat()
        pysatwcnf = pysatcnf.weighted()
        pysatwcnf.wght = self.weights
        return pysatwcnf
