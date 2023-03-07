import os
import json
import subprocess
from typing import Tuple

from k_sat.solver import Solver
from formula.formula import Formula

class WalkSATlm(Solver):
	""" Python interface for WalkSATlm solver [Cai15]"""
	def __init__(self, formula: Formula, seed: int = 42, p: float = 0.15, w1: float = 6.0, w2: float = 5.0) -> None:
		"""Python interface for WalkSATlm solver [Cai15]

		Args:
			formula (Formula): Formula to find satisfying assignment for.
			seed (int, optional): Random seed for number generation. Defaults to 42.
			p (float, optional): Probability of choosing variable to flip in clause randomly. Defaults to 0.15.
			w1 (float, optional): Weight of make1 score function. Defaults to 6.0.
			w2 (float, optional): Weight of make2 score function. Defaults to 5.0.
		"""

		self.formula = formula
		self.seed = seed
		self.p = p
		self.w1 = w1
		self.w2 = w2

	def sat(self, timeout: int = 10000) -> Tuple[str, int]:
		"""Finds statisfying assignment of formula.

		Args:
			timeout (int, optional): Timeout for algorithm if no satisfying assignment found yet. Defaults to 10000.

		Returns:
			Tuple[str, int]: Tuple of satisfying assignment and runtime to find it.
		"""

		# Convert formula to pysat to use to_file functionality
		formula_ps = self.formula.to_pysat()

		# Use correct directory
		parent_dir = os.path.dirname(os.getcwd())
		dir = f'{parent_dir}/k_sat/walkSATlm/binaries' 

		# Write formula to file
		cnf_filename = f'{dir}/formula.cnf'
		formula_ps.to_file(cnf_filename)

		# Call c++ binary
		cmd_str = f'./WalkSatlm2013 formula.cnf {self.seed} {self.p} {self.w1} {self.w2} {timeout}'
		subprocess.run(cmd_str, shell=True, cwd = dir, stdout=subprocess.DEVNULL)

		# Parse result
		res_filename = f'{dir}/result.json'
		json_result = json.load(open(res_filename, 'r'))
		assignment = ''.join([str(x) for x in json_result["result"]])
		runtime = json_result["steps"]

		# Save result
		self.assignment = assignment
		self.runtime = runtime

		# Clean up by deleting files
		os.remove(cnf_filename)
		os.remove(res_filename)

		return assignment, runtime


