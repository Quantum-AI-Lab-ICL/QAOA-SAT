from typing import List
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
