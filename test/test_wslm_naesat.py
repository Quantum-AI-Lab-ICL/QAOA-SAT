import random
import unittest
from formula.nae.naef import NAEFormula
from formula.nae.nae_clause import NAEClause
from formula.variable import Variable
from benchmark.cnf.random_cnf import RandomCNF
from k_sat.walkSATlm.wslm_solver import WSlmSolver

class TestWSLM(unittest.TestCase):

	def setUp(self):
		self.problem_gen = RandomCNF(type='knaesat')

	def test_returns_knaesat(self):
		wslm = WSlmSolver()

		for n in range(12, 16):
			problems = self.problem_gen.from_poisson(n, 3, satisfiable=True, instances=5)

			for problem in problems:
				ass, _ = wslm.sat(problem)
				self.assertTrue(problem.is_satisfied(ass), f'WSLM returned non satisfying assignment')

	def test_make_knaesat_basic(self):
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

		wslm = WSlmSolver(makes={1:5.0})

		# Should make c1, i.e. score of 5
		score, _ = wslm.score(f, 0, "001")
		self.assertTrue(score == 5, f'Invalid make score, expected {5}, actual {score}')

		# Should make c1, i.e. score of 5
		score, _ = wslm.score(f, 1, "001")
		self.assertTrue(score == 5, f'Invalid make score, expected {5}, actual {score}')

		# Should make c3, i.e. score of 5
		score, _ = wslm.score(f, 2, "010")
		self.assertTrue(score == 5, f'Invalid make score, expected {5}, actual {score}')

		c4 = NAEClause([x0])
		fnae = NAEFormula([c4])

		# Should make c1 because this is independent of NAE formulation
		scorenae, _ = wslm.score(fnae, 0, "0")
		self.assertTrue(scorenae == 5, f'Invalid make score, expected {5}, actual {scorenae}')

	def test_make_knaesat(self):
		# Set weight of make1 to 1 and breakk to 1
		wslm = WSlmSolver(makes={1:1}, breaks={0:1})

		for n in range(12, 16):
			for k in range(3, 6):
				problems = self.problem_gen.from_poisson(n, k, satisfiable=True, instances=5)

				for problem in problems:
					# Random assignment
					bs = problem.random_assignment()

					# Random variable
					v_id = random.randint(0, n - 1)
					mb1, _ = wslm.score(problem, v_id, bs)

					# Flipped assignment
					f_bs = wslm.flip(v_id, bs)

					# make(v) is how many clauses newly satisfied
					unsat_curr = set(problem.unsatisfied_clauses(bs))
					unsat_flip = set(problem.unsatisfied_clauses(f_bs))
					make = len(list(unsat_curr - unsat_flip))

					# In k-NAE-SAT formulation, make(v) = make1(v) + breakk(v)
					self.assertEqual(mb1, make, f'make1 {mb1}, make {make}')

	def test_lmake_knaesat(self):
		x0 = Variable(0, False)
		x1 = Variable(1, False) 
		x2 = Variable(2, False) 

		n_x0 = Variable(0, True)
		n_x1 = Variable(1, True) 
		n_x2 = Variable(2, True) 

		c1 = NAEClause([x0, n_x2])
		c2 = NAEClause([x0, x1])
		c3 = NAEClause([x0, n_x1, x2])

		f = NAEFormula([c1, c2, c3])

		wslm = WSlmSolver()

		# Should make_1 c2 and make_2 c1 + c3 i.e. score of 5 + 6 * 2 = 17
		score, _ = wslm.score(f, 0, "000")
		self.assertTrue(score == 17, f'Invalid make score, expected {17}, actual {score}')

		# Should make_2 c2, i.e. score of 6
		score, _ = wslm.score(f, 1, "100")
		self.assertTrue(score == 6, f'Invalid make score, expected {6}, actual {score}')

		# Should make_3 c3, i.e. score of 0
		score, _ = wslm.score(f, 2, "100")
		self.assertTrue(score == 0, f'Invalid make score, expected {0}, actual {score}')

	def test_break_knaesat_basic(self):
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

		wslm = WSlmSolver(makes={}, breaks={1:5.0})

		# Should break c3, i.e. score of 5
		score, _ = wslm.score(f, 1, "000")
		self.assertEqual(score, 5, f'Invalid break score, expected {5}, actual {score}')

		# Should break c1, i.e. score of 1
		score, _ = wslm.score(f, 2, "000")
		self.assertEqual(score, 5, f'Invalid break score, expected {5}, actual {score}')

		# Should break2 c1, i.e. score of 0 since we are only considering break1
		score, _ = wslm.score(f, 2, "100")
		self.assertEqual(score, 0, f'Invalid break score, expected {0}, actual {score}')

	def test_break_knaesat(self):
		# Set weight of make_{k} to 1 and break1 to 1
		wslm = WSlmSolver(makes={0:1}, breaks={1:1})

		for n in range(12, 16):
			for k in range(3, 6):
				problems = self.problem_gen.from_poisson(n, k, satisfiable=True, instances=5)

				for problem in problems:
					# Random assignment
					bs = problem.random_assignment()

					# Random variable
					v_id = random.randint(0, n - 1)
					score, basic_break = wslm.score(problem, v_id, bs)

					# Flipped assignment
					f_bs = wslm.flip(v_id, bs)

					# break(v) is how many clauses newly unsatisfied
					unsat_curr = set(problem.unsatisfied_clauses(bs))
					unsat_flip = set(problem.unsatisfied_clauses(f_bs))
					break_acc = len(list(unsat_flip - unsat_curr))

					# In k-SAT formulation, break(v) = break1(v) + make_{k}(v)
					self.assertEqual(score, break_acc, f'score {score}, break {break_acc}')

					# Also check basic_break is correct
					self.assertEqual(score, basic_break, f'score {score}, basic_break {break_acc}')

	def test_make_break_symmetry(self):
		wslm = WSlmSolver(makes={1:1}, breaks={1:-1})

		for n in range(12, 16):
			for k in range(3, 6):
				problems = self.problem_gen.from_poisson(n, k, satisfiable=True, instances=5)

				for problem in problems:
					# Random assignment
					bs = problem.random_assignment()

					# Random variable
					v_id = random.randint(0, n - 1)
					mb, _ = wslm.score(problem, v_id, bs)

					# Flip to get -v
					bs = wslm.flip(v_id, bs)
					mbf, _ = wslm.score(problem, v_id, bs)

					# make_tau(v) = break_tau(-v)
					# => make_tau(v) - break_tau(v) = - (make_tau(-v) - break_tau(-v))
					self.assertEqual(mb, -1 * mbf)