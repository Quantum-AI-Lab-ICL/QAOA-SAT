import random
import unittest
from formula.nae.naef import NAEFormula
from formula.nae.nae_clause import NAEClause
from formula.variable import Variable
from benchmark.cnf.random_cnf import RandomCNF
from k_sat.walkSATlm.wslm_balance_solver import WSlmBalanceSolver

class TestWSLMBalance(unittest.TestCase):

	def setUp(self):
		self.problem_gen = RandomCNF(type='knaesat')

	def test_returns_knaesat(self):
		wslm = WSlmBalanceSolver()

		for n in range(12, 16):
			problems = self.problem_gen.from_poisson(n, 3, satisfiable=True, instances=5)

			for problem in problems:
				ass, _ = wslm.sat(problem)
				self.assertTrue(problem.is_satisfied(ass), f'WSLM returned non satisfying assignment')

	def test_balance_scoring(self):
		x0 = Variable(0, False)
		x1 = Variable(1, False) 
		x2 = Variable(2, False) 

		n_x0 = Variable(0, True)
		n_x1 = Variable(1, True) 
		n_x2 = Variable(2, True) 

		c1 = NAEClause([x0, x1, n_x2])
		c2 = NAEClause([n_x0, x1])
		c3 = NAEClause([x0, n_x1, x2])

		f = NAEFormula([c1, c2, c3])

		wslm = WSlmBalanceSolver()

		# Expected:
		# c1: all literals false -(0-3)^2 = -9
		# c2: 1 literal false 1 literal true -(1-1)^2 = 0
		# c3: 1 literal false 2 literals true -(2-1)^2 = -1
		balance, _ = wslm.score(f, 2, "000")
		self.assertEqual(balance, -10, f'Invalid balance, expected {-10}, actual {balance}')

		# Expected:
		# c1: 2 literals false 1 literal true  -(1-2)^2 = -1
		# c2: all literals true -(0-2)^2 = -4
		# c3: 2 literals false 1 literal true -(1-2)^2 = -1
		balance, _ = wslm.score(f, 1, "001")
		self.assertEqual(balance, -6, f'Invalid make score, expected {-6}, actual {balance}')