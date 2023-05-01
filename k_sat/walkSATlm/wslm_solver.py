from typing import Dict, Tuple
import random
import numpy as np
from scipy.stats import bernoulli

from formula.cnf.cnf import CNF
from k_sat.solver import Solver


class WSlmSolver(Solver):
	
	def __init__(
		self, p: float = 0.15, makes: Dict[int, float] = None, breaks: Dict[int, float] = None
		) -> None:
		"""Python implementation of WalkSATlm solver [Cai15] can be used for KSAT or KNAESAT.

		Args:
			p (float, optional): Noise. Defaults to 0.15.
			makes (Dict[int, float], optional): Make levels and corresponding weights to use in linear score. 
				Defaults to 6.0 * make_1 + 5.0 * make_2.
			breaks (Dict[int, float], optional): Break levels and corresponding weights to use in linear score.
				Here, break_l = break(k - l). Defaults to None.
		"""

		self.noise = bernoulli(p)
		if makes is None:
			makes = {1 : 5.0, 2 : 6.0}
		if breaks is None:
			breaks = {}
		self.make_levels = np.array(list(makes.keys()), dtype=np.uint8)
		self.make_weights = np.array(list(makes.values()), dtype=np.float32)
		self.break_levels = np.array(list(breaks.keys()), dtype=np.uint8)
		self.break_weights = np.array(list(breaks.values()), dtype=np.float32)

	def flip(self, index: int, ass: str) -> str:
		"""Return assignment with index flipped.

		Args:
			index (int): Index to flip.
			ass (str): Current assignment.

		Returns:
			str: Assignment with flip.
		"""
		return [a if not i == index else '0' if a == '1' else '1' for i, a in enumerate(ass)]


	def score(self, formula: CNF, v_id: int, curr_ass: str) -> Tuple[float, float]:
		"""Find variable score.

		Args:
			formula (CNF): Formula.
			v_id (int): Variable id.
			curr_ass (str): Current variable assignments.

		Returns:
			Tuple[float, float]: Score and base break.
		"""

		# One method to avoid duplicate computation. The most expensive action for these large
		# problems is iterating through the clauses and finding which variables are satisfied.
		# I.e. we only iterate once and calculate everything we need.

		# Initialise levels
		makes = np.empty_like(self.make_levels)
		breaks = np.empty_like(self.break_levels)

		# Flip variable
		flip_ass = self.flip(v_id, curr_ass)

		# Base break
		bbreak = 0

		for clause in formula.clauses:

			# Base broken if sat -> unsat
			bbreak += clause.is_satisfied(curr_ass) and not clause.is_satisfied(flip_ass)
			
			curr_sat = 0
			flip_sat = 0
			for variable in clause.variables:
				if variable.is_satisfied(curr_ass):
					curr_sat += 1
				if variable.is_satisfied(flip_ass):
					flip_sat += 1
			
			k = clause.num_vars

			for i, tau in enumerate(self.make_levels):
				makes[i] += curr_sat == (tau - 1) and flip_sat == tau
			
			for i, tau in enumerate(self.break_levels):
				breaks[i] += curr_sat == (k - tau) and flip_sat == (k - tau - 1)

		return np.dot(self.break_weights, breaks) + np.dot(self.make_weights, makes), bbreak

	def sat(self, formula: CNF, timeout: int = None) -> Tuple[str, int]:
		"""Finds statisfying assignment of formula.

		Args:
			formula (CNF): Formula to find satisfying assignment for.
			timeout (int, optional): Timeout for algorithm if no satisfying assignment found yet. Defaults to None (keep going until solution found).

		Returns:
			Tuple[str, int]: Tuple of satisfying assignment and runtime to find it. String set to "-1" formula unsatisfiable/solver timed out.
		"""

		# Start with random assignment
		curr_ass = formula.random_assignment()

		# Currently unsatisfied clauses
		unsat_clauses = formula.unsatisfied_clauses(curr_ass)

		runtime = 0

		# TODO: runtime? timeout?
		while len(unsat_clauses) > 0 and timeout >= 0:
			runtime += 1

			# Randomly select an unsatisfied clause 
			curr_clause = random.choice(unsat_clauses)

			# Check if any variable has break = 0 
			bbreaks = np.zeros(shape=(curr_clause.num_vars, ))
			scores = np.zeros(shape=(curr_clause.num_vars, ))
			for i, variable in enumerate(curr_clause.variables):
				score, bbreak = self.score(formula, variable.id, curr_ass) 

				if bbreak == 0:
					curr_ass = self.flip(variable.id, curr_ass)
					break

				bbreaks[i] = bbreak
				scores[i] = score

			# No freebies
			if self.noise.rvs(1) == 1:
				# Choose variable at random to flip
				rand_var = random.choice(curr_clause.variables)
				curr_ass = self.flip(rand_var.id, curr_ass)
			else:
				# Find variable(s) with minimum break
				min_breaks = np.argmin(bbreaks)

				# Decide which to flip
				if len(min_breaks) == 1:
					# Flip unique minimum
					min_var = curr_clause.get_variable(min_breaks[0])
					curr_ass = self.flip(min_var.id, curr_ass)
				else:
					# Settle tiebreaks with score
					max_scores = np.argmax(scores)

					# Choose randomly from maximums (should only really be 1)
					max_var = curr_clause.get_variable(random.choice(max_scores))
					curr_ass = self.flip(max_var.id, curr_ass) 
		
		return curr_ass, runtime