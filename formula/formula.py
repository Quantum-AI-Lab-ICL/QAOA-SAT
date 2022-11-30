from abc import ABC, abstractmethod
from typing import List
from formula.clause import Clause


class Formula(ABC):
    @abstractmethod
    def __init__(self, clauses: List[Clause]) -> None:
        raise NotImplementedError(
            "Attempted initialisation of abstract base formula class"
        )

    @abstractmethod
    def is_satisfied(self, assignment: str) -> bool:
        raise NotImplementedError(
            "Attempted invocation of abstract base formula class method"
        )
