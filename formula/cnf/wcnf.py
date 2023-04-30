from formula.cnf import CNF
from formula.cnf.disjunctive_clause import DisjunctiveClause
from typing import List, Tuple
from pysat.formula import WCNF as PySATWCNF


class WCNF(CNF):
    def __init__(
        self, clauses: List[DisjunctiveClause] = None, weights: List[float] = None
    ) -> None:
        """Weighted CNF formula.

        Args:
            clauses (List[Clause], optional): Clauses of formula. Defaults to None.
            weights (List[float], optional): Weights of clauses. Defaults to all clause weights set to 1.
        """
        super().__init__(clauses)
        if weights is None and clauses is not None:
            weights = [1 for _ in clauses]
        self.weights = weights

    @property
    def weighted_clauses(self) -> List[Tuple[DisjunctiveClause, float]]:
        """Zipped clauses and weights

        Returns:
            List[Tuple[Clause, float]]: List of zipped clauses and weights.
        """
        return zip(self.clauses, self.weights)

    def append(self, clause: DisjunctiveClause, weight: float = 1) -> None:
        """Add new clause to end of formula with corresponding weight.

        Args:
            clause (Clause): Clause to be added to end of formula.
            weight (float, optional): Weight of clause. Defaults to 1.
        """
        super().append(clause)
        self.weights.append(weight)

    def assignment_weight(self, assignment: str) -> float:
        """Weight of assignment (sum of weights of unsatisfied clauses).

        Args:
            assignment (str): Assignment of variables in clauses.

        Returns:
            float: Weight of assignment.
        """
        return sum(
            [w * (not c.is_satisfied(assignment)) for (c, w) in self.weighted_clauses]
        )

    def to_pysat(self) -> PySATWCNF:
        """Convert to PySAT representation of formula.

        Returns:
            PySATWCNF: PySAT representation of formula.
        """
        pysatcnf = super().to_pysat()
        pysatwcnf = pysatcnf.weighted()
        pysatwcnf.wght = self.weights
        return pysatwcnf
