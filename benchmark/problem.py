from abc import ABC, abstractmethod

class Problem(ABC):
	"""Class to represent problem instance"""

	@abstractmethod
	def __init__(self, n: int, m: int, k: int) -> None:
		"""Create problem instance

		Args:
			n (int): Number of variables
			m (int): Number of clauses
			k (int): Variables per clause
		"""
		pass

	@abstractmethod
	def assignment_weight(self, assignment:str) -> float:
		"""Calculate weight of assignment on problem instance.

		Args:
			assignment (str): Bitstring representing assignment.

		Returns:
			float: Weight of assignment.
		"""
		pass