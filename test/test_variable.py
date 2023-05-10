import unittest
from formula.variable import Variable

class TestVariable(unittest.TestCase):
	def test_is_satisfied(self):
		# Positive literals
		v1 = Variable(0, False)
		self.assertTrue(v1.is_satisfied("1"))
		self.assertFalse(v1.is_satisfied("0"))

		# Negated literals	
		nv1 = Variable(0, True)
		self.assertTrue(nv1.is_satisfied("0"))
		self.assertFalse(nv1.is_satisfied("1"))
		
		# Variable within multiple assignments
		self.assertTrue(v1.is_satisfied("101"))
		self.assertFalse(v1.is_satisfied("010"))
		
		# Make sure assert thrown (string too short for variable position)
		v2 = Variable(1, False)
		with self.assertRaises(AssertionError):
			v2.is_satisfied("1")

	def test_init(self):
		# Test initialization with positive variable
		v1 = Variable(0, False)
		self.assertEqual(v1.id, 0)
		self.assertEqual(v1.is_negation, False)

		# Test initialization with negated variable
		v2 = Variable(1, True)
		self.assertEqual(v2.id, 1)
		self.assertEqual(v2.is_negation, True)

