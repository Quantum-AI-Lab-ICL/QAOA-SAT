from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
from typing import Callable, Dict

class ClassicalSolver:

	def __init__(self):
		"""PySAT implementation of RC2 SAT-solver"""

	def max_sat(self, wcnf: WCNF, weight_func: Callable[[str], float], ret_num:int = 10) -> Dict[str, float]:
		"""Calculates maximally satisfying assignments.

		Args:
			wcnf (WCNF): Weighted formula to satisfy.
			weight_func (Callable[[str], float]): Function to calculate weight of assignment.
			ret_num (int, optional): Number of solutions to return. Defaults to 10.

		Returns:
			Dict[str, float]: Maximally satisyfing solutions with corresponding weights.
		"""

		rc2 = RC2(wcnf)
		max_sats = {}

		for _ in range(ret_num):
			model = rc2.compute()
			# Convert assignments to bitstring
			ass = ''.join(['1' if x > 0 else '0' for x in model])
			# Calculate assignment weight using function callable parameter
			max_sats[ass] = weight_func(ass)
			# Add negation to prompt next solution
			rc2.add_clause([-l for l in model])

		return max_sats