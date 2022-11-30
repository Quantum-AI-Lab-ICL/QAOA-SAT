from typing import List
from formula.formula import Formula
from formula.clause import Clause
from formula.variable import Variable
from pysat.formula import CNF as PySATCNF


class CNF(Formula):
    def __init__(self, clauses: List[Clause]) -> None:
        self.clauses = clauses
        self.max_var = 0
        for clause in clauses:
            for var in clause.variables:
                if var.id > max_var:
                    max_var = var.id

    @property
    def num_vars(self) -> int:
        return self.max_var

    def append(self, clause: Clause) -> None:
        self.clauses.append(clause)
        for var in clause.variables:
            if var.id > max_var:
                max_var = var.id

    def __repr__(self) -> str:
        return "∧\n".join([c.__str__() for c in self.clauses]) + "\n"

    def __str__(self) -> str:
        return "∧\n".join([c.__str__() for c in self.clauses]) + "\n"

    def get_clause(self, index: int) -> Variable:
        return self.clauses[index]

    def is_satisfied(self, assignment: str) -> bool:
        assert len(assignment) == self.num_vars
        return all([c.is_satisfied for c in self.clauses])

    def to_pysat(self) -> PySATCNF:
        pysatcnf = PySATCNF()
        for clause in self.clauses:
            pysatclause = []
            for var in clause.variables:
                # PySat starts numbering at 1
                pysatvar = var.id + 1
                if var.is_negation():
                    # Pysat uses negative to indicate negation
                    pysatvar = -1 * pysatvar
                pysatclause.append(pysatvar)
            pysatcnf.append(pysatclause)
        return pysatcnf
