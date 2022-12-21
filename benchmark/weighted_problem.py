from typing import Dict, List
from benchmark.problem import Problem
from formula.wcnf import WCNF
from pysat.formula import WCNF as PySATWCNF
from max_3_sat.solver import Solver
import numpy as np


class WeightedProblem(Problem):
    """Class to create weighted problem instances for benchmarking"""

    def __init__(self, n: int, m: int, k: int, weights: List[float] = None) -> None:
        """Create problem instance for benchmarking

        Args:
            n (int): Number of variables
            m (int): Number of clauses
            k (int): Variables per clause
            weights (List[float], optional): Clause weights. Defaults to random weights in the interval (0, 1).
        """

        super().__init__(n, m, k)

        if weights is None:
            weights = np.random.uniform(0, 10, m)

        self.formula = WCNF(self.formula.clauses, weights)

    def weight_ratio(self, solver1: Solver, solver2: Solver) -> float:
        """Weight ratio of two different solvers on problem instance.

        Args:
            solver1 (Solver): First solver
            solver2 (Solver): Second solver

        Returns:
            float: Ratio of satisfying weight of maximal solutions of solvers.
        """
        # TODO: Discuss this metric. Just one?

        sol1 = list(solver1.max_sat(ret_num=1).values())[0]
        sol2 = list(solver2.max_sat(ret_num=1).values())[0]

        return sol1 / sol2
