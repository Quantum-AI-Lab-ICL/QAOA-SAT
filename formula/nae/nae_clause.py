from typing import List

from formula.cnf.disjunctive_clause import DisjunctiveClause
from formula.variable import Variable


class NAEClause(DisjunctiveClause):
	
	def __init__(self, variables: List[Variable] = None) -> None:
		"""Class representing a disjunctive clause within a NAE formula.

		Args:
			variables (List[Variable], optional): Variables within clause. Defaults to None.
		"""
		super().__init__(variables)

	def is_satisfied(self, assignment: str) -> bool:
		"""Determines whether clause is satisfied by assignment.

		Args:
			assignment (str): Assignment for variables.

		Returns:
			bool: True iff clause is satisfied
		"""

		# NAE clause satisfied iff at least one literal true and not all literals assigned to same truth value
		return super().is_satisfied(assignment) and not super().all_same(assignment)