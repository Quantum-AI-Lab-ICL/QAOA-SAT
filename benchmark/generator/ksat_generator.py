from typing import List
import os
import h5py
from pysat.solvers import Glucose4

from benchmark.generator.generator import Generator
from formula.formula import Formula
from formula.variable import Variable
from formula.cnf import CNF
from benchmark.ratios import sat_ratios


class KSATGenerator(Generator):

    def __init__(self) -> None:
        """Generator for random k-sat problems. """
        pass


    def filename(self, n: int, k: int, index: int = 0, suffix: str = "cnf") -> str:
        """Get filename corresponding to CNF problem.

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.
            index (int, optional): File index. Defaults to 0.
            suffix (int, optional): File suffix. Defaults to cnf.

        Returns:
            str: Filename corresponding to CNF problem.
        """
        dir = self.directory(n, k)
        cnf_filename = f'{dir}/f_n{n}_k{k}_{index}.{suffix}'
        return cnf_filename

    def directory(self, n: int, k: int) -> str:
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

    def from_file(self, n: int, k: int, index: int = 0, calc_naive: bool = False) -> Formula:
        """Get problem from file.

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.
            index (int, optional): File index. Defaults to 0.
            calc_naive (bool, optional): Read in unsat counts. Defaults to False.

        Returns:
            Formula: Problem instance.
        """
        cnf_filename = self.filename(n, k, index)
        counts_filename = self.filename(n, k, index, 'hdf5')
        cnf = CNF.from_file(cnf_filename)
        if calc_naive:
            with h5py.File(counts_filename, 'r') as f:
                cnf.counts = f.get('counts')[:]
        return cnf

    def variables_from_count(self, c: int) -> List[Variable]:
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

    def is_satisfiable(self, f: Formula) -> bool:
        """Verify if formula is satisfiable.

        Args:
            f (Formula): Formula to check satisfiability of.

        Returns:
            bool: Boolean variable set to true iff formula is satisfiable.
        """

        with Glucose4(bootstrap_with=f.to_pysat().clauses) as g:
            return g.solve()
    
    def ratio(self, k: int) -> float:
        """Satisfiability ratio for k-SAT problem.

        Args:
            k (int): Variables per clause.

        Returns:
            float: Satisfiability ratio for value of k.
        """

        return sat_ratios[k] 

    def empty_formula(self) -> Formula:
        """Empty formula.

        Returns:
            Formula: Empty formula.
        """

        return CNF()
