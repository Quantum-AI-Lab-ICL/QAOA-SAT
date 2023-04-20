from pysat.solvers import Glucose4
import os
import h5py

from benchmark.generator.ksat_generator import KSATGenerator
from benchmark.ratios import nae_sat_ratios
from formula.cnf import CNF
from formula.formula import Formula
from formula.nae_cnf import NAECNF

class KNAESATGenerator(KSATGenerator):
    
    def __init__(self) -> None:
        """Generator for random k-nae-sat problems. """
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
        # Offset due to condor jobs (not worth redoing/naming)
        offset = 100000
        return super().filename(n, k, index + offset, suffix)

    def directory(self, n: int, k: int) -> str:
        """Get directory corresponding to CNF problem type.

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.

        Returns:
            str: Filename corresponding to CNF type.
        """
        if os.getenv('MACHINE') == 'LAB':
            return f'/vol/bitbucket/ae719/instances/knaesat/k_{k}/n_{n}'
        else:
            parent_dir = os.path.dirname(os.getcwd())
            return f"{parent_dir}/benchmark/instances/knaesat/k_{k}/n_{n}"

    def from_file(self, n: int, k: int, calc_naive: bool = False, index: int = 0) -> Formula:
        """Get problem from file.

        Args:
            n (int): Number of variables per instance.
            k (int): Variables per clause per instance.
            calc_naive (bool, optional): Read in unsat counts. Defaults to False.
            index (int, optional): File index. Defaults to 0.

        Returns:
            Formula: Problem instance.
        """
        # TODO: if redo condor job, get rid of this method...
        cnf_filename = self.filename(n, k, index)
        counts_filename = self.filename(n, k, index, 'hdf5')
        cnf = NAECNF.from_file(cnf_filename)
        if calc_naive:
            with h5py.File(counts_filename, 'r') as f:
                counts = f.get('counts')[:]
                # NAE counts as h(x) + h(-x)
                cnf.counts = counts + counts[::-1]
        return cnf

    def is_satisfiable(self, f: NAECNF) -> bool:
        """Verify if formula is NAE satisfiable.

        Args:
            f (NAECNF): Formula to check satisfiability of.

        Returns:
            bool: Boolean variable set to true iff formula is satisfiable.
        """

        with Glucose4(bootstrap_with=f.to_pysat().clauses) as g:
            for x in g.enum_models():
                # Checks x satisfies f in NAE formulation
                bs = [1 if v > 0 else 0 for v in x]
                if f.is_satisfied(bs):
                    return True
        return False

    def ratio(self, k: int) -> float:
        """Satisfiability ratio for k-NAE-SAT problem.

        Args:
            k (int): Variables per clause.

        Returns:
            float: Satisfiability ratio for value of k.
        """
        return nae_sat_ratios[k] 

    def empty_formula(self) -> Formula:
        """Empty formula.

        Returns:
            Formula: Empty formula.
        """

        return NAECNF()
