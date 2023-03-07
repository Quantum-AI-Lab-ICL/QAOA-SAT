from abc import ABC, abstractmethod
from typing import Tuple
from formula.formula import Formula


class Solver(ABC):
    def __init__(self, formula: Formula):
        """Abstract Solver class to be extended."""
        super.__init__()

    @abstractmethod
    def sat(self, timeout: int = None) -> Tuple[str, int]:
        """Finds statisfying assignment of formula.

        Args:
            timeout (int, optional): Timeout for algorithm if no satisfying assignment found yet. Defaults to None.

        Returns:
            Tuple[str, int]: Tuple of satisfying assignment and runtime to find it.
        """
        pass