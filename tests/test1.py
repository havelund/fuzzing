import unittest
from tests.testutils import *
from src.fuzzing.temporal_logic import *


class FuzzTestSuite1(BaseTestSuite):
    def setUp(self):
        # Set up the common test data (initial state)
        self.test = [
            {'name': 'C0', 'zone': 'a0', 'mode': 'b0'},
            {'name': 'C1', 'zone': 'a1', 'mode': 'b1'},
            {'name': 'C2', 'zone': 'a2', 'mode': 'b2'},
            {'name': 'C3', 'zone': 'a3', 'mode': 'b3'},
            {'name': 'C4', 'zone': 'a4', 'mode': 'b4'},
            {'name': 'C5', 'zone': 'a5', 'mode': 'b5'},
            {'name': 'C6', 'zone': 'a6', 'mode': 'b6'},
            {'name': 'C7', 'zone': 'a7', 'mode': 'b7'},
            {'name': 'C8', 'zone': 'a8', 'mode': 'b8'},
            {'name': 'C9', 'zone': 'a9', 'mode': 'b9'},
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
        self.false(Until(TRUE, N('C10')))

    def test_case_6(self):
        self.true(Until(TRUE, N('C9')))

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
        self.true(FollowedBy(N('C3'), N('C7')))

    def test_case_13(self):
        self.false(FollowedBy(N('C3'), N('C2')))

    def test_case_14(self):
        self.true(CountFuture(Or(N('C1'), N('C3')), 2, 2))
        self.false(CountFuture(Or(N('C1'), N('C3')), 3, 3))

    def test_case_15(self):
        count_formula = CountPast(Or(N('C2'), N('C4')), 2, 2)
        formula = Always(Implies(N('C5'), count_formula))
        self.true(formula)


if __name__ == '__main__':
    unittest.main()