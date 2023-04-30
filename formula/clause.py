from abc import ABC, abstractmethod, abstractproperty
from typing import List

from formula.variable import Variable

class Clause(ABC):
	
	@abstractmethod
	def __init__(self, variables: List[Variable] = None) -> None:
		"""Class representing a clause within a Boolean formula.

		Args:
			variables (List[Variable], optional): Variables within clause. Defaults to None.

		Raises:
			NotImplementedError: Attempted initialisation of abstract base formula class.
		"""
		raise NotImplementedError(
			"Attempted initialisation of abstract base clause class"
		)

	@abstractproperty
	def num_vars(self) -> int:
		"""Number of variables in clause.

		Returns:
			int: Number of variables in clause.

		Raises:
			NotImplementedError: Attempted initialisation of abstract base formula class.
		"""
		raise NotImplementedError(
			"Attempted initialisation of abstract base clause class"
		)

	@abstractmethod
	def append(self, variable: Variable) -> None:
		"""Add variable to end of clause.

		Args:
			variable (Variable): Variable to add to end of clause.

		Raises:
			NotImplementedError: Attempted initialisation of abstract base formula class.
		"""
		raise NotImplementedError(
			"Attempted initialisation of abstract base clause class"
		)

	@abstractmethod
	def get_variable(self, index: int) -> Variable:
		"""Get variable at index position in clause.

		Args:
			index (int): Position of variable to retrieve. Starts at 0.

		Returns:
			Variable: Variable at index position in clause.

		Raises:
			NotImplementedError: Attempted initialisation of abstract base formula class.
		"""
		raise NotImplementedError(
			"Attempted initialisation of abstract base clause class"
		)

	@abstractmethod
	def is_satisfied(self, assignment: str) -> bool:
		"""Determines whether clause is satisfied by assignment.

		Args:
			assignment (str): Assignment for variables.

		Returns:
			bool: True iff clause is satisfied

		Raises:
			NotImplementedError: Attempted initialisation of abstract base formula class.
		"""
		raise NotImplementedError(
			"Attempted initialisation of abstract base clause class"
		)

	@abstractmethod
	def all_same(self, assignment: str) -> bool:
		"""Determines whether literals in clause all set to same truth value.

		Args:
			assignment (str): Assignment for variables.

		Returns:
			bool: True iff all literals set to same truth value.

		Raises:
			NotImplementedError: Attempted initialisation of abstract base formula class.
		"""
		raise NotImplementedError(
			"Attempted initialisation of abstract base clause class"
		)