import unittest
from basic.src.fuzz import *


class FuzzTestSuite(unittest.TestCase):

    def equal(self, tc: TestConstraint, result: bool):
        self.assertEqual(apply_test_constraint(tc, self.test), result)

    def true(self, tc: TestConstraint):
        self.equal(tc, True)

    def false(self, tc: TestConstraint):
        self.equal(tc, False)

    def setUp(self):
        # Set up the common test data (initial state)
        self.test = [
            {'name': 'C0', 'args': {'zone': 'b1', 'mode': 'c3'}},
            {'name': 'C1', 'args': {'zone': 'c3', 'mode': 'd1'}},
            {'name': 'C2', 'args': {'zone': 'e1', 'mode': 'a2'}},
            {'name': 'C3', 'args': {'zone': 'c3', 'mode': 'd1'}},
            {'name': 'C4', 'args': {'zone': 'a3', 'mode': 'b3'}},
            {'name': 'C5', 'args': {'zone': 'a3', 'mode': 'b3'}},
            {'name': 'C6', 'args': {'zone': 'a3', 'mode': 'b3'}},
            {'name': 'C7', 'args': {'zone': 'a3', 'mode': 'b3'}},
            {'name': 'C8', 'args': {'zone': 'a3', 'mode': 'b3'}},
            {'name': 'C9', 'args': {'zone': 'a3', 'mode': 'b3'}},
        ]

    def test_case_1(self):
        self.true(Always(Implies(N('C1'), Eventually(N('C2')))))

    def test_case_2(self):
        self.false(Not(N('C0')))

    def test_case_3(self):
        self.true(N('C0'))

    def test_case_4(self):
        self.true(Always(Implies(N('C4'), Until(Not(N('C1')), N('C9')))))

    def test_case_5(self):
        self.false(Until(T, N('C10')))

    def test_case_6(self):
        self.true(Until(T, N('C9')))

    def test_case_7(self):
        self.true(Until(Not(N('C8')), And(N('C3'), Next(N('C4')))))

    def test_case_8(self):
        self.false(Until(Not(N('C8')), And(N('C3'), Next(N('C5')))))

    def test_case_9(self):
        self.true(Until(Not(N('C8')), And(N('C3'), Eventually(N('C8')))))

    def test_case_10(self):
        self.false(Or(Eventually(N('C50')), Eventually(N('C51'))))

    def test_case_11(self):
        self.true(Or(Eventually(N('C50')), Eventually(N('C5'))))

    def test_case_12(self):
        self.true(response(N('C3'), N('C7')))

    def test_case_13(self):
        self.false(response(N('C3'), N('C2')))


if __name__ == '__main__':
    unittest.main()
