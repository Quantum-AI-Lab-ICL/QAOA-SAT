from formula.clause import Clause
from formula.variable import Variable
from formula.cnf import CNF
from pysat.formula import CNF as PySATCNF
import numpy as np


class Problem:
    """Class to create problem instances for benchmarking"""

    def __init__(self, n: int, m: int, k: int) -> None:
        """Create problem instance for benchmarking

        Args:
            n (int): Number of variables
            m (int): Number of clauses
            k (int): Variables per clause
        """

        # TODO: remove multiple of 2 when randomness fixed
        if 2 * n > m * k:
            raise RuntimeError("More variables specified than formula can hold")

        # Set up formula
        cnf = CNF()

        # Set up variables
        variables = []
        for i in range(n):
            variables.append(Variable(id=i, is_negation=False))
            variables.append(Variable(id=i, is_negation=True))

        # Randomly create clauses and append to cnf
        # TODO: actually make random

        # First use up all variables
        variables_unused = variables.copy()
        while len(variables_unused) > 0:
            clause = Clause()
            for i in range(k):
                rand_index = np.random.randint(0, len(variables_unused))
                rand_var = variables_unused[int(rand_index)]
                clause.append(rand_var)  # pylint complains about int
                variables_unused.remove(rand_var)
                if len(variables_unused) <= 0:
                    for _ in range(k - i - 1):
                        clause.append(rand_var)
                    break
            cnf.append(clause)

        # Now fill in the rest randomly
        for _ in range(m - len(cnf.clauses)):
            clause = Clause()
            while clause.num_vars < 3:
                rand_index = np.random.randint(0, 2 * n)
                clause.append(variables[int(rand_index)])  # pylint complains about int
            cnf.append(clause)

        self.formula = cnf
