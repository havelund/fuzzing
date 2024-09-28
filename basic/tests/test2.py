import unittest
from basic.tests.testutils import *
from basic.src.fuzz import *


class FuzzTestSuite2(BaseTestSuite):
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
            {'name': 'C7', 'zone': 'a2', 'mode': 'b7'},
            {'name': 'C8', 'zone': 'a8', 'mode': 'b8'},
            {'name': 'C9', 'zone': 'a2', 'mode': 'b6'},
        ]

    def test_case_1(self):
        self.true(Always(
            Implies(
                N('C2'),
                FreezeVar(
                    'zone',
                    Eventually(
                        Now(lambda e, c: name(c) == 'C7' and zone(c) == zone(e))
                    )
                )
            )
        ))

    def test_case_2(self):
        self.true(Always(
            Implies(
                N('C2'),
                FreezeVar(
                    'zone',
                    Eventually(
                        And(
                            N('C6'),
                            FreezeVar(
                                'mode',
                                Eventually(
                                    Now(lambda e, c: name(c) == 'C9' and
                                                     zone(c) == zone(e) and
                                                     mode(c) == mode(e))
                                )
                            )
                        )
                    )
                )
            )
        ))


if __name__ == '__main__':
    unittest.main()
