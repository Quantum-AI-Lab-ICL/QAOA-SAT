import unittest
from formula.variable import Variable
from formula.cnf.disjunctive_clause import DisjunctiveClause

class TestDisjunctiveClause(unittest.TestCase):

    def setUp(self) -> None:
        self.v0 = Variable(0, False)
        self.nv0 = Variable(0, True)
        self.v1 = Variable(1, False)
        self.nv1 = Variable(1, True)
        self.v2 = Variable(2, False)
        self.v3 = Variable(3, False)
        self.v4 = Variable(4, False)

    def test_init(self) -> None:
        clause = DisjunctiveClause()
        self.assertEqual(clause.variables, [])

		# Clause removes duplicates
        clause = DisjunctiveClause([self.v0, self.v1, self.v0])
        self.assertEqual(clause.variables, [self.v0, self.v1])

        clause = DisjunctiveClause([self.v2, self.v3, self.v4])
        self.assertEqual(clause.variables, [self.v2, self.v3, self.v4])

    def test_num_vars(self) -> None:
        clause = DisjunctiveClause([self.v0, self.v1, self.v2])
        self.assertEqual(clause.num_vars, 3)

        clause = DisjunctiveClause([self.v3, self.v4])
        self.assertEqual(clause.num_vars, 2)

		# Clause removes duplicates
        clause = DisjunctiveClause([self.v0, self.v1, self.v0])
        self.assertEqual(clause.num_vars, 2)

    def test_append(self) -> None:
        clause = DisjunctiveClause([self.v0, self.v1, self.v2])
        clause.append(self.v3)
        self.assertEqual(clause.variables, [self.v0, self.v1, self.v2, self.v3])

		# No effect when variable already in clause appended
        clause.append(self.v0)
        self.assertEqual(clause.variables, [self.v0, self.v1, self.v2, self.v3])

    def test_get_variable(self) -> None:
        clause = DisjunctiveClause([self.v1, self.v2, self.v4])
        self.assertEqual(clause.get_variable(0), self.v1)
        self.assertEqual(clause.get_variable(1), self.v2)
        self.assertEqual(clause.get_variable(2), self.v4)

    def test_is_satisfied(self) -> None:
        clause = DisjunctiveClause([self.v0, self.v1])
        self.assertTrue(clause.is_satisfied("01"))
        self.assertTrue(clause.is_satisfied("10"))
        self.assertTrue(clause.is_satisfied("11"))
        self.assertFalse(clause.is_satisfied("00"))

        clause = DisjunctiveClause([self.v0, self.nv1])
        self.assertTrue(clause.is_satisfied("00"))
        self.assertTrue(clause.is_satisfied("10"))
        self.assertTrue(clause.is_satisfied("11"))
        self.assertFalse(clause.is_satisfied("01"))

    def test_all_same(self) -> None:
        clause = DisjunctiveClause([self.v0, self.v1])
        self.assertFalse(clause.all_same("01"))
        self.assertFalse(clause.all_same("10"))
        self.assertTrue(clause.all_same("11"))
        self.assertTrue(clause.all_same("00"))

        clause = DisjunctiveClause([self.nv0, self.v1])
        self.assertFalse(clause.all_same("00"))
        self.assertFalse(clause.all_same("11"))
        self.assertTrue(clause.all_same("01"))
        self.assertTrue(clause.all_same("10"))

    def test_parity(self) -> None:
        clause = DisjunctiveClause([self.v0, self.v1])
        self.assertEqual(clause.parity(), 1)
        self.assertEqual(clause.parity([self.v0]), -1)
        self.assertEqual(clause.parity([self.v1]), -1)
        self.assertEqual(clause.parity([self.v0, self.v1]), 1)

        clause = DisjunctiveClause([self.nv0, self.v1])
        self.assertEqual(clause.parity(), -1)
        self.assertEqual(clause.parity([self.nv0]), 1)
        self.assertEqual(clause.parity([self.v1]), -1)
        self.assertEqual(clause.parity([self.nv0, self.v1]), -1)