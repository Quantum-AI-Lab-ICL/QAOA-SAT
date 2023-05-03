import unittest
from benchmark.cnf.random_cnf import RandomCNF

class TestRandomCNF(unittest.TestCase):

	def setUp(self):
		self.random_cnf = RandomCNF(type='ksat')

	def test_is_satisfiable(self):
		pass
