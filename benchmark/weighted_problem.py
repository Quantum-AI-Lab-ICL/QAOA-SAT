from typing import Dict, List
from benchmark.problem import Problem
from formula.wcnf import WCNF
from pysat.formula import WCNF as PySATWCNF
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
            weights = [np.random.rand() * 10 for _ in range(m)]

        self.formula = WCNF(self.formula.clauses, weights)
    

    def approximation_ratio(self, q_sols: Dict[str, float], c_sols: Dict[str, float]) -> float:
        """Calculate approximation ratio of best quantum to best classical solution.

        Args:
            q_sols (Dict[str, float]): Quantum solutions ordered by weight.
            c_sols (Dict[str, float]): Classical solutions ordered by weight.

        Returns:
            float: Approximation ratio
        """

        # TODO: Discuss this metric

        return list(q_sols.values())[0] / list(c_sols.values())[0]

