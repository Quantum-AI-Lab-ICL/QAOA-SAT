from typing import List
from formula.variable import Variable
from functools import reduce


class Clause:
    def __init__(self, variables: List[Variable]) -> None:
        self.variables = variables

    @property
    def num_vars(self) -> int:
        return len(self.variables)

    def __repr__(self) -> str:
        return "(" + " ∨ ".join([v.__str__() for v in self.variables]) + ")"

    def __str__(self) -> str:
        return "(" + " ∨ ".join([v.__str__() for v in self.variables]) + ")"

    def get_variable(self, id: int) -> Variable:
        return self.variables[id]

    def is_satisfied(self, assignment: str) -> bool:
        return any([v.is_satisfied(assignment) for v in self.variables])

    def parity(self, vars: List[Variable] = None) -> int:
        if vars is None:
            vars = self.variables
        r = reduce(lambda x, y: x ^ y, [not v.is_negation for v in vars], False)
        return -1 if r else 1
