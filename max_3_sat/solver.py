from abc import ABC, abstractmethod

class Solver(ABC):

	def __init__(self):
		"""Abstract Solver class to be extended."""
		super.__init__()

	@abstractmethod
	def max_sat(self, ret_num: int = 1):
		"""Finds maximally statisfying assignments of formula.

		Args:
			ret_num (int, optional): Number of assignments to return. Defaults to 1.
		"""
		pass