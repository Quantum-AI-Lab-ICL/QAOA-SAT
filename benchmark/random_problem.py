import pathos            
import os
import numpy as np
from typing import List
from benchmark.generator.knaesat_generator import KNAESATGenerator
from benchmark.generator.ksat_generator import KSATGenerator
from functools import partial

from formula.cnf import CNF
from formula.formula import Formula
from formula.clause import Clause
from benchmark.generator.generator import Generator

class RandomProblem:
    
	def __init__(self, type: str = None, generator: Generator = None) -> None:
		"""Create random problem instances for benchmarking.

		Args:
			type (str, optional): Type of generator to use if one not provided. Defaults to None.
			generator (Generator, optional): Generator to use. Defaults to None.

		Raises:
			RuntimeError: Must either provide generator or generator type.
			RuntimeError: Generator type not recognised.
		"""
		if generator is None and type is None:
			raise RuntimeError("Must either provide generator or generator type")
		
		if generator is not None:
			self.generator = generator
		elif type == 'ksat':
			self.generator = KSATGenerator()
		elif type == 'knaesat':
			self.generator = KNAESATGenerator()
		else:
			raise RuntimeError("Generator type not recognised")

	def from_poisson(
		self, n: int, k: int, r: int = None, satisfiable=True, instances: int = 1, from_file: int = None, calc_naive: bool = False, parallelise: bool = False
	) -> List[Formula]:
		"""Create problem instance as per [BM22]:

		Args:
			n (int): Number of variables per instance.
			k (int): Variables per clause per instance.
			r (int, optional): Clauses to variables ratio for poisson method. Defaults to satisfiability ratio.
			satisfiable (bool) : Ensures the instances generated are satisfiable. Defaults to True.
			instances (int): Number of instances to generate. Defaults to 1.
			from_file (int): If not None, retrieve from previously generated files starting at index provided. Defaults to None.
			calc_naive (bool): Find number of unsatisfied clauses per bistring in formulas. Defaults to False.
			parallelise (bool): Parallelise creation. Defaults to False.

		Returns:
			List[Formula]: Random problem instances created using poisson method.
		"""

		if from_file is not None:
			
			# Retrieve instances from previously written files
			indices = [i + from_file for i in range(instances)]
			if parallelise:
				with pathos.multiprocessing.Pool(os.cpu_count() - 1) as executor:
					cnfs = list(executor.map(partial(self.generator.from_file, n=n, k=k, calc_naive=calc_naive), indices))
			else:
				cnfs = [self.generator(n, k, i, calc_naive) for i in indices] 

		else:
			# Use approximate satisfiability if r not specified
			if r is None:
				r = self.generator.ratio(k)

			def generate(t: int):
				if t < 0:
					raise RuntimeError("Avoiding stack overflow, check satisfiability.")
				# Set up formula
				cnf = self.generator.empty_formula()

				# Set up variables
				variables = self.generator.variables_from_count(n)

				# Uniformly sample from variables
				m = np.random.poisson(r * n)
				for _ in range(m):
					clause = Clause()
					for _ in range(k):
						rand_index = int(np.random.randint(0, 2 * n))
						clause.append(variables[rand_index])
					cnf.append(clause)

				# If formula not satisfiable, try again
				if satisfiable and not self.generator.is_satisfiable(cnf):
					print("Unsatisfiable formula generated, trying again")
					# t to avoid stack overflow!
					return generate(t-1)

				if calc_naive:
					cnf.naive_counts

				return cnf

			# Set satisfiability tries to 100 to avoid stack overflow
			gs = [100 for _ in range(instances)]
			if parallelise:
				with pathos.multiprocessing.Pool(os.cpu_count() - 1) as executor:
					cnfs = list(executor.map(generate, gs))
			else:
				cnfs = [generate(t) for t in gs] 

		return cnfs

	def from_exhaustive(
		self, n: int, m: int, k: int, satisfiable=False, instances: int = 1
	) -> List[Formula]:
		"""Create problem instances as follows:
			- Uniformly choose at random from $\{x_0, ~x_0, ... x_{n-1}, ~x_{n-1}\}$ without replacement until all used
			- Uniformly choose at random from ${x_0, ~x_0, ... x_{n-1}, ~x_{n-1}\}$ with replacement
			- Ensures clauses have $k$ different literals (not necessarily different variables, e.g. can suffer from LEM)

		Args:
			n (int): Number of variables per instance.
			m (int): Number of clauses per instance.
			k (int): Variables per clause per instance.
			satisfiable (bool): Ensures the instances generated are satisfiable. Defaults to False.
			instances (int): Number of instances to generate. Defaults to 1.

		Raises:
			RuntimeError: More variables specified than formula can hold.

		Returns:
			CNF: Random problem instances created using 'exhaustive' method.
		"""
		if n > m * k:
			raise RuntimeError("More variables specified than formula can hold")

		cnfs = []
		i = 0
		while i < instances:

			# Set up formula
			cnf = self.generator.empty_formula()

			# Set up variables
			variables = self.generator.variables_from_count(n)

			# First use up all ids
			ids_unused = list(range(n))
			while len(ids_unused) > 0:
				clause = Clause()
				for _ in range(k):
					# All ids used up
					if len(ids_unused) == 0:
						cnf.append(clause)
						break
					# Choose id randomly and remove
					rand_id = np.random.choice(ids_unused)
					ids_unused.remove(rand_id)
					# Choose if negation randomly
					negation = np.random.binomial(1, 0.5, 1)
					# Access variable
					rand_var = variables[int(2 * rand_id + negation)]
					clause.append(rand_var)
				cnf.append(clause)

			# Now fill in the rest randomly
			for _ in range(m - len(cnf.clauses)):
				clause = Clause()
				for _ in range(k):
					rand_var = np.random.choice(variables)
					clause.append(rand_var)
				cnf.append(clause)

			# If formula not satisfiable, try again
			if satisfiable and not self.generator.is_satisfiable(cnf):
				print("Unsatisfiable formula generated, trying again")
				continue

			# If formula is satisfiable, save it
			cnfs.append(cnf)
			i += 1

		return cnfs