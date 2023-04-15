from pysat.solvers import Glucose4
import os

from benchmark.generator.ksat_generator import KSATGenerator
from formula.cnf import CNF
from benchmark.ratios import nae_sat_ratios

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
		dir = self.directory(n, k)
		cnf_filename = f'{dir}/f_n{n}_k{k}_{index + offset}.{suffix}'
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
			return f'/vol/bitbucket/ae719/instances/knaesat/k_{k}/n_{n}'
		else:
			parent_dir = os.path.dirname(os.getcwd())
			return f"{parent_dir}/benchmark/instances/knaesat/k_{k}/n_{n}"

	def is_satisfiable(self, f: CNF) -> bool:
		"""Verify if formula is NAE satisfiable.

		Args:
			f (CNF): Formula to check satisfiability of.

		Returns:
			bool: Boolean variable set to true iff formula is satisfiable.
		"""

		# Bitstring x NAE satisfies if both x and -x satisfy
		with Glucose4(bootstrap_with=f.to_pysat().clauses) as g:
			for x in g.enum_models():
				# Check if -x satisfies
				nx = ['1' if v < 0 else '0' for v in x]
				if f.is_satisfied(nx):
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