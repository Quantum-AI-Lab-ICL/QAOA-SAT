from pysat.formula import WCNF
from max_3_sat.solver import Solver
from pysat.examples.rc2 import RC2
from typing import Callable, Dict


class ClassicalSolver(Solver):
    def __init__(self, wcnf: WCNF, weight_func: Callable[[str], float]) -> None:
        """PySAT implementation of RC2 SAT-solver

            Args:
                wcnf (WCNF): Weighted formula to satisfy.
                weight_func (Callable[[str], float]): Function to calculate weight of assignment.

        Raises:
            RuntimeError: Invalid 3SAT formula
        """
        if any([len(c) > 3 for c in wcnf.soft]):
            raise RuntimeError("Instance of non-3-SAT passed to 3SAT solver")

        self.wcnf = wcnf
        self.weight_func = weight_func

    def max_sat(self, ret_num: int = 1) -> Dict[str, float]:
        """Calculates maximally satisfying assignments.

        Args:
            ret_num (int, optional): Number of solutions to return. Defaults to 10.

        Returns:
            Dict[str, float]: Maximally satisyfing solutions with corresponding weights.
        """

        rc2 = RC2(self.wcnf)
        max_sats = {}

        for _ in range(ret_num):
            model = rc2.compute()
            # Convert assignments to bitstring
            ass = "".join(["1" if x > 0 else "0" for x in model])
            # Calculate assignment weight using function callable parameter
            max_sats[ass] = self.weight_func(ass)
            # Add negation to prompt next solution
            rc2.add_clause([-l for l in model])

        return max_sats
