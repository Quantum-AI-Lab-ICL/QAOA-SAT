from typing import List, Tuple
import random

from formula.cnf.disjunctive_clause import DisjunctiveClause
from formula.cnf.cnf import CNF
from formula.variable import Variable
from k_sat.solver import Solver


class WSlmSolver(Solver):
	
	def __init__(
		self, seed: int = 42, p: float = 0.15, w1: float = 6.0, w2: float = 5.0
	) -> None:
		"""Python implementation of WalkSATlm solver [Cai15]

		Args:
			seed (int, optional): Random seed for number generation. Defaults to 42.
			p (float, optional): Probability of choosing variable to flip in clause randomly (noise). Defaults to 0.15.
			w1 (float, optional): Weight of make1 score function. Defaults to 6.0.
			w2 (float, optional): Weight of make2 score function. Defaults to 5.0.
		"""

		self.seed = seed
		self.p = p
		self.w1 = w1
		self.w2 = w2

	def score(self, formula: CNF, v_id: Variable, curr_ass: str, level: Tuple[int, int]) -> Tuple[int, int, int]:
		"""Find break and make for all levels specified. 

		Args:
			formula (CNF): Formula.
			v_id (int): Variable id.
			curr_ass (str): Current variable assignments.
			level (Tuple[int, int]): Tuple of level for break and level for make.

		Returns:
			Tuple[int, int, int]: Tuple of break, make1 and make2 of variable v_id.
		"""
		# Flip variable
		flip_ass = [a if not i == v_id else '0' if a == '1' else '1' for i, a in enumerate(curr_ass)]

		# Find clauses that break
		b, m1, m2 = 0, 0, 0
		for clause in formula.clauses:

			# Find satisfactions
			curr_sat = clause.is_satisfied(curr_ass)
			flip_sat = clause.is_satisfied(flip_ass)
			
			# break if sat -> unsat
			b += curr_sat and not flip_sat

			# make1 if unsat -> sat
			m1 += not curr_sat and flip_sat

		return b, m1, None



	def sat(self, formula: CNF, timeout: int = None) -> Tuple[str, int]:

		# Start with random assignment
		curr_ass = formula.random_assignment()

		# Currently unsatisfied clauses
		unsat_clauses = formula.unsatisfied_clauses(curr_ass)

		# TODO: runtime? timeout?
		while len(unsat_clauses) > 0 and timeout >= 0:

			# Randomly select an unsatisfied clause 
			curr_clause = random.choice(unsat_clauses)

			# Check if any variable has break(v) = 0 
			for v_id in range(formula.num_vars):
				broken_clauses = self.vbreak() 




		

