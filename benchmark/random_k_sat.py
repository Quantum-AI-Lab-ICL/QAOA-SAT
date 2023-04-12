from typing import List
import os
import numpy as np
from pysat.solvers import Glucose4
from pathos.multiprocessing import ProcessingPool as Pool
import h5py
import torch 
import pathos            

from formula.clause import Clause
from formula.variable import Variable
from formula.cnf import CNF
from benchmark.ratios import sat_ratios


class RandomKSAT:
    """Class to create random problem instances for benchmarking"""

    def __init__(self, n: int, k: int, r: float, cnfs: List[CNF]) -> None:
        """Create problem instances for benchmarking.

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.
            r (float): Clause density per instance.
            cnfs (CNF): Formulas of instances.
        """

        self.n = n
        self.k = k
        self.r = r
        self.formulas = cnfs

    @classmethod
    def filename(cls, n: int, k: int, index: int = 0, suffix: str = "cnf") -> str:
        """Get filename corresponding to CNF problem.

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.
            index (int, optional): File index. Defaults to 0.
            suffix (int, optional): File suffix. Defaults to cnf.

        Returns:
            str: Filename corresponding to CNF problem.
        """
        dir = RandomKSAT.directory(n, k)
        cnf_filename = f'{dir}/f_n{n}_k{k}_{index}.{suffix}'
        return cnf_filename

    @classmethod
    def directory(cls, n: int, k: int) -> str:
        """Get directory corresponding to CNF problem type.

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.

        Returns:
            str: Filename corresponding to CNF type.
        """
        if os.getenv('MACHINE') == 'LAB':
            return f'/vol/bitbucket/ae719/instances/ksat/k_{k}/n_{n}'
        else:
            parent_dir = os.path.dirname(os.getcwd())
            return f"{parent_dir}/benchmark/instances/ksat/k_{k}/n_{n}"

    @classmethod
    def variables_from_count(cls, c: int) -> List[Variable]:
        """Generate $\{x_0, ~x_0, ... x_{c-1}, ~x_{c-1}\}$

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
    def is_satisfiable(cls, f: CNF) -> bool:
        """Verify if formula is satisfiable.

        Args:
            f (CNF): Formula to check satisfiability of.

        Returns:
            bool: Boolean variable set to true iff formula is satisfiable.
        """

        g = Glucose4()
        g.append_formula(f.to_pysat())
        return g.solve()


    @classmethod
    def from_exhaustive(
        cls, n: int, m: int, k: int, satisfiable=False, instances: int = 1
    ) -> None:
        """Create problem instances as follows:
            - Uniformly choose at random from $\{x_0, ~x_0, ... x_{n-1}, ~x_{n-1}\}$ without replacement until all used
            - Uniformly choose at random from ${x_0, ~x_0, ... x_{n-1}, ~x_{n-1}\}$ with replacement
            - Ensures clauses have $k$ different literals (not necessarily different variables, e.g. can suffer from LEM)

        Args:
            n (int): Number of variables per instance.
            m (int): Number of clauses per instance.
            k (int): Variables per clause per instance.
            satisfiable (bool): Ensures the instances generated are satisfiable. Defaults to False.
            instances (int): Number of instances to generate. Defaults to 1.

        Raises:
            RuntimeError: More variables specified than formula can hold.

        Returns:
            CNF: Random problem instances created using 'exhaustive' method.
        """
        if n > m * k:
            raise RuntimeError("More variables specified than formula can hold")

        cnfs = []
        i = 0
        while i < instances:

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

            # If formula not satisfiable, try again
            if satisfiable and not RandomKSAT.is_satisfiable(cnf):
                print("Unsatisfiable formula generated, trying again")
                continue

            # If formula is satisfiable, save it
            cnfs.append(cnf)
            i += 1

        return cls(n, k, n/m, cnfs)

    @classmethod
    def from_poisson(
        cls, n: int, k: int, r: int = None, satisfiable=True, instances: int = 1, from_file: int = None, calc_naive: bool = False, parallelise: bool = False
    ) -> None:
        """Create problem instance as per [BM22]:

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.
            r (int, optional): Clauses to variables ratio for poisson method. Defaults to satisfiability ratio.
            satisfiable (bool) : Ensures the instances generated are satisfiable. Defaults to True.
            instances (int): Number of instances to generate. Defaults to 1.
            from_file (int): If not None, retrieve from previously generated files starting at index provided. Defaults to None.
            calc_naive (bool): Find number of unsatisfied clauses per bistring in formulas. Defaults to False.
            parallelise (bool): Parallelise creation. Defaults to False.

        Returns:
            CNF: Random problem instances created using poisson method.
        """

        if from_file is not None:
            
            def retrieve(index):
                cnf_filename = RandomKSAT.filename(n, k, index)
                cnf = CNF.from_file(cnf_filename)

                # Retrieve unsat clauses counts
                if calc_naive:
                    counts_filename = RandomKSAT.filename(n, k, index, 'hdf5')
                    with h5py.File(counts_filename, 'r') as f:
                        cnf.counts = torch.from_numpy(f.get('counts')[:])
                return cnf

            # Retrieve instances from previously written files
            indices = [i + from_file for i in range(instances)]
            if parallelise:
                with pathos.multiprocessing.Pool(os.cpu_count() - 1) as executor:
                    cnfs = list(executor.map(retrieve, indices))
            else:
                cnfs = [retrieve(i) for i in indices] 

        else:
            # Use approximate satisfiability if r not specified
            if r is None:
                r = sat_ratios[k]

            def generate(t: int):
                if t < 0:
                    raise RuntimeError("Avoiding stack overflow, check satisfiability.")
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

                # If formula not satisfiable, try again
                if satisfiable and not RandomKSAT.is_satisfiable(cnf):
                    print("Unsatisfiable formula generated, trying again")
                    # t to avoid stack overflow!
                    return generate(t-1)

                if calc_naive:
                    cnf.naive_counts

                return cnf

            # Set satisfiability tries to 100 to avoid stack overflow
            gs = [100 for _ in range(instances)]
            if parallelise:
                with pathos.multiprocessing.Pool(os.cpu_count() - 1) as executor:
                    cnfs = list(executor.map(generate, gs))
            else:
                cnfs = [generate(t) for t in gs] 

        return cls(n, k, r, cnfs)
