from typing import Tuple
import random

from formula.cnf.disjunctive_clause import DisjunctiveClause
from formula.cnf.cnf import CNF
from k_sat.solver import Solver


class WSSolver(Solver):
	
	def __init__(self, p: float = 0.15) -> None:
		"""Python implementation of WalkSATlm solver [Cai15].

		Args:
			p (float, optional): Noise. Defaults to 0.15.
		"""

		self.p = p

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




		

