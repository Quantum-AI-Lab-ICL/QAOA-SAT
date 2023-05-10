from typing import Tuple
from k_sat.walkSATlm.wslm_solver import WSlmSolver
from formula.nae.naef import NAEFormula


class WslmBalanceSolver(WSlmSolver):

	def __init__(self, p: float = 0.15) -> None:
		"""WalkSatlm implementation for NAE-SAT problem where scoring is based on how balanced each clause is.

		Args:
			p (float, optional): Noise. Defaults to 0.15.
		"""
		super().__init__(p, {}, {})

	def score(self, formula: NAEFormula, v_id: int, curr_ass: str) -> Tuple[float, float]:
		"""Find variable score.

		Args:
			formula (NAEFormula): Formula.
			v_id (int): Variable id.
			curr_ass (str): Current variable assignments.

		Returns:
			Tuple[float, float]: Score and base break.
		"""

		# Flip variable
		flip_ass = self.flip(v_id, curr_ass)

		# Base break
		bbreak = 0

		balance = 0

		for clause in formula.clauses:

			# Base broken if sat -> unsat
			bbreak += clause.is_satisfied(curr_ass) and not clause.is_satisfied(flip_ass)

			# Calculate c^T to get |c^T - c^F| = |2c^T - k|
			cT = sum([v.is_satisfied(flip_ass) for v in clause.variables])
			balance -= (2 * cT - clause.num_vars)**2

		return balance, bbreak


			


