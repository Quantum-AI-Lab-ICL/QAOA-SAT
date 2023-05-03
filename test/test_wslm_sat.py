import unittest
from formula.cnf.cnf import CNF
from formula.nae.naef import NAEFormula
from formula.cnf.disjunctive_clause import DisjunctiveClause
from formula.variable import Variable
from benchmark.cnf.random_cnf import RandomCNF
from k_sat.walkSATlm.wslm_solver import WSlmSolver

class TestWSLM(unittest.TestCase):

	def setUp(self):
		self.problem_gen = RandomCNF(type='ksat')

	def test_returns_ksat(self):
		wslm = WSlmSolver()

		for n in range(12, 16):
			problems = self.problem_gen.from_poisson(n, 3, satisfiable=True, instances=5)

			for problem in problems:
				ass, _ = wslm.sat(problem)
				self.assertTrue(problem.is_satisfied(ass), f'WSLM returned non satisfying assignment')

	def test_make_ksat(self):
		x0 = Variable(0, False)
		x1 = Variable(1, False) 
		x2 = Variable(2, False) 

		n_x0 = Variable(0, True)
		n_x1 = Variable(1, True) 
		n_x2 = Variable(2, True) 

		c1 = DisjunctiveClause([x0, x1, n_x2])
		c2 = DisjunctiveClause([n_x0, x1])
		c3 = DisjunctiveClause([x0, n_x1, x2])

		f = CNF([c1, c2, c3])

		wslm = WSlmSolver(makes={1:5.0})

		# Should make c1, i.e. score of 5
		scorex0, _ = wslm.score(f, 0, "001")
		self.assertTrue(scorex0 == 5, f'Invalid make score, expected {5}, actual {scorex0}')

		# Should make c1, i.e. score of 5
		scorex1, _ = wslm.score(f, 1, "001")
		self.assertTrue(scorex1 == 5, f'Invalid make score, expected {5}, actual {scorex1}')

		# Should make c3, i.e. score of 5
		scorex2, _ = wslm.score(f, 2, "010")
		self.assertTrue(scorex2 == 5, f'Invalid make score, expected {5}, actual {scorex2}')

	def test_lmake_ksat(self):
		x0 = Variable(0, False)
		x1 = Variable(1, False) 
		x2 = Variable(2, False) 

		n_x0 = Variable(0, True)
		n_x1 = Variable(1, True) 
		n_x2 = Variable(2, True) 

		c1 = DisjunctiveClause([x0, n_x2])
		c2 = DisjunctiveClause([x0, x1])
		c3 = DisjunctiveClause([x0, n_x1, x2])

		f = CNF([c1, c2, c3])

		wslm = WSlmSolver()

		# Should make_1 c2 and make_2 c1 + c3 i.e. score of 5 + 6 * 2 = 17
		scorex0, _ = wslm.score(f, 0, "000")
		self.assertTrue(scorex0 == 17, f'Invalid make score, expected {17}, actual {scorex0}')

		# Should make_2 c2, i.e. score of 6
		scorex1, _ = wslm.score(f, 1, "100")
		self.assertTrue(scorex1 == 6, f'Invalid make score, expected {6}, actual {scorex1}')

		# Should make_3 c3, i.e. score of 0
		scorex2, _ = wslm.score(f, 2, "100")
		self.assertTrue(scorex2 == 0, f'Invalid make score, expected {0}, actual {scorex2}')