from formula.clause import Clause
from formula.variable import Variable
from formula.cnf import CNF
from formula.wcnf import WCNF
from benchmark.problem import Problem
from typing import List
from benchmark.ratios import sat_ratios
from max_3_sat.solver import Solver
import numpy as np


class RandomKSAT(Problem):
    """Class to create random problem instances for benchmarking"""

    def __init__(self, n: int, m: int, k: int, cnf: CNF, weighted: bool = False) -> None:
        """Create problem instance for benchmarking
        Args:
            n (int): Number of variables.
            m (int): Number of clauses.
            k (int): Variables per clause.
            cnf (CNF): Formula for problem.
            weighted (bool): Assign weights to clauses

        """

        self.n = n
        self.m = m
        self.k = k

        if weighted:
            weights = np.random.uniform(0, n * m / k, m)
            self.formula = WCNF(cnf.clauses, weights)
        else:
            self.formula = cnf

    @classmethod
    def variables_from_count(cls, c: int) -> List[Variable]:
        """ Generate $\{x_0, ~x_0, ... x_{c-1}, ~x_{c-1}\}$

        Args:
            count (int): Id to generate up to.

        Returns:
            List[Variable]: $\{x_0, ~x_0, ... x_{c-1}, ~x_{c-1}\}$
        """
        variables = []
        for i in range(c):
            variables.append(Variable(id=i, is_negation=False))
            variables.append(Variable(id=i, is_negation=True))

        return variables

    @classmethod
    def from_exhaustive(cls, n: int, m: int, k: int, weighted: bool = False) -> None:
        """Create problem instance as follows:
            - Uniformly choose at random from $\{x_0, ~x_0, ... x_{n-1}, ~x_{n-1}\}$ without replacement until all used
            - Uniformly choose at random from ${x_0, ~x_0, ... x_{n-1}, ~x_{n-1}\}$ with replacement
            - Ensures clauses have $k$ different literals (not necessarily different variables, e.g. can suffer from LEM) 

        Args:
            n (int): Number of variables
            m (int): Number of clauses
            k (int): Variables per clause
            weighted (bool): Assigns weights to clauses

        Raises:
            RuntimeError: More variables specified than formula can hold.

        Returns:
            CNF: Random problem instance created using 'exhaustive' method.
        """
        if n > m * k:
            raise RuntimeError("More variables specified than formula can hold")

        # Set up formula
        cnf = CNF()

        # Set up variables
        variables = RandomKSAT.variables_from_count(n)

        # First use up all ids
        ids_unused = list(range(n))
        while len(ids_unused) > 0:
            clause = Clause()
            for _ in range(k):
                # All ids used up
                if len(ids_unused) == 0:
                    cnf.append(clause)
                    break
                # Choose id randomly and remove
                rand_id = np.random.choice(ids_unused)
                ids_unused.remove(rand_id)
                # Choose if negation randomly
                negation = np.random.binomial(1, 0.5, 1)
                # Access variable
                rand_var = variables[int(2 * rand_id + negation)]
                clause.append(rand_var)  
            cnf.append(clause)

        # Now fill in the rest randomly
        for _ in range(m - len(cnf.clauses)):
            clause = Clause()
            for _ in range(k):
                rand_var = np.random.choice(variables)
                clause.append(rand_var)
            cnf.append(clause)

        return cls(n, m, k, cnf, weighted)

    @classmethod
    def from_poisson(cls, n: int, k: int, r: int = None, weighted: bool = False) -> None:
        """Create problem instance as per [BM22] (see notebook):

        Args:
            n (int): Number of variables.
            k (int): Variables per clause.
            r (int, optional): Clauses to variables ratio for poisson method. Defaults to satisfiability ratio.
            weighted (bool): Assigns weights to clauses

        Returns:
            CNF: Random problem instance created using poisson method.
        """
        # Use approximate satisfiability if r not specified
        if r is None:
            r = sat_ratios[k]

        # Set up formula
        cnf = CNF()

        # Set up variables
        variables = RandomKSAT.variables_from_count(n)

        # Uniformly sample from variables
        m = np.random.poisson(r * n)
        for _ in range(m):
            clause = Clause()
            for _ in range(k):
                rand_index = int(np.random.randint(0, 2 * n))
                clause.append(variables[rand_index])
            cnf.append(clause)

        return cls(n, m, k, cnf, weighted)

    def assignment_weight(self, assignment:str) -> float:
        """Calculate weight of assignment on problem instance.

        Args:
            assignment (str): Bitstring representing assignment.

        Returns:
            float: Weight of assignment.
        """
        if len(assignment) != self.n:
            raise RuntimeError(f'Invalid assignment: expected length {n}, actual length {len(assignment)}')

        return self.formula.assignment_weight(assignment)

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

