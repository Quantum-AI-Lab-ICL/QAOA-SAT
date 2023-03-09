from abc import ABC, abstractmethod
from typing import Tuple
from formula.formula import Formula


class Solver(ABC):
    def __init__(self):
        """Abstract Solver class to be extended."""
        super.__init__()

    @abstractmethod
    def sat(self, formula: Formula, timeout: int = None) -> Tuple[str, int]:
        """Finds statisfying assignment of formula.

        Args:
                        formula (Formula): Formula to find satisfying assignment for.
            timeout (int, optional): Timeout for algorithm if no satisfying assignment found yet. Defaults to None (keep going until solution found).

        Returns:
            Tuple[str, int]: Tuple of satisfying assignment and runtime to find it. String set to "-1" formula unsatisfiable/solver timed out.
        """
        pass
