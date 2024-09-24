import unittest
from basic.fuzz import *


class FuzzTestSuite(unittest.TestCase):

    def setUp(self):
        # Set up the common test data (initial state)
        self.test = [
            ('C0', [('zone', 'd1'), ('mode', 'e2')]),
            ('C1', [('zone', 'd1'), ('mode', 'e2')]),
            ('C2', [('zone', 'e3'), ('mode', 'a2')]),
            ('C3', [('zone', 'c2'), ('mode', 'd3')]),
            ('C4', [('zone', 'b2'), ('mode', 'c2')]),
            ('C5', [('zone', 'a2'), ('mode', 'b1')]),
            ('C6', [('zone', 'a2'), ('mode', 'b1')]),
            ('C7', [('zone', 'a2'), ('mode', 'b1')]),
            ('C8', [('zone', 'a2'), ('mode', 'b1')]),
            ('C9', [('zone', 'a2'), ('mode', 'b1')])
        ]

    def test_case_1(self):
        self.assertEqual(Always(Implies(N('C1'), Eventually(N('C2'))))(self.test), True)

    def test_case_2(self):
        self.assertEqual(Not(N('C0'))(self.test), False)

    def test_case_3(self):
        self.assertEqual(N('C0')(self.test), True)

    def test_case_4(self):
        self.assertEqual(Always(Implies(N('C4'), Until(Not(N('C1')), N('C9'))))(self.test), True)

    def test_case_5(self):
        self.assertEqual(Until(T, N('C10'))(self.test), False)

    def test_case_6(self):
        self.assertEqual(Until(T, N('C9'))(self.test), True)

    def test_case_7(self):
        self.assertEqual(Until(Not(N('C8')), And(N('C3'), Next(N('C4'))))(self.test), True)

    def test_case_8(self):
        self.assertEqual(Until(Not(N('C8')), And(N('C3'), Next(N('C5'))))(self.test), False)

    def test_case_9(self):
        self.assertEqual(Until(Not(N('C8')), And(N('C3'), Eventually(N('C8'))))(self.test), True)

    def test_case_10(self):
        self.assertEqual(Or(Eventually(N('C50')), Eventually(N('C51')))(self.test), False)

    def test_case_11(self):
        self.assertEqual(Or(Eventually(N('C50')), Eventually(N('C5')))(self.test), True)

    def test_case_12(self):
        self.assertEqual(response(N('C3'), N('C7'))(self.test), True)

    def test_case_13(self):
        self.assertEqual(response(N('C3'), N('C2'))(self.test), False)


if __name__ == '__main__':
    unittest.main()
