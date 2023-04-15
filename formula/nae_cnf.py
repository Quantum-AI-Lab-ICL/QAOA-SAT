import numpy as np
from typing import Iterable, List

from formula.clause import Clause
from formula.cnf import CNF


class NAECNF(CNF):

	def __init__(self, clauses: List[Clause] = None) -> None:
		super().__init__(clauses)

	@property
	def naive_sats(self) -> Iterable[int]:
		"""Finds all satisfying bitstrings in NAE formulation. 
		Where x satisfies NAESAT iff x and -x satisfy SAT.
		Use singleton pattern to only evaluate once.

		Returns:
			Iterable[int]: Value at index 1 iff bitstring satisfies, in bistring order.

		"""
		if self.sats is None:
			sats = super().naive_sats
			nsats = 2 ** self.num_vars - 1 - sats
			self.sats = np.intersect1d(sats, nsats)
		return self.sats

	@property
	def naive_counts(self) -> Iterable[int]:
		"""Finds number of unsatisfied clauses for all bitstrings in NAE formulation.
		Where h^NAE(x) = h(x) + h(-x)
		Use singleton pattern to only evaluate once.

		Returns:
			Iterable[int]: Number of unsatisfied clauses in bistring order.
		"""
		if self.counts is None:
			counts = super().naive_counts
			self.counts = counts + counts[::-1]
		return self.counts
