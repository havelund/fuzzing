
import unittest
from basic.tests.testutils import *
from basic.src.fuzz import *


class FuzzTestSuite2(BaseTestSuite):
    def setUp(self):
        # Set up the common test data (initial state)
        self.test = [
            {'name': 'C0', 'args': {'zone': 'a0', 'mode': 'b0'}},
            {'name': 'C1', 'args': {'zone': 'b1', 'mode': 'c1'}},
            {'name': 'C2', 'args': {'zone': 'c2', 'mode': 'd2'}},
            {'name': 'C3', 'args': {'zone': 'd3', 'mode': 'e3'}},
            {'name': 'C4', 'args': {'zone': 'e4', 'mode': 'a4'}},
            {'name': 'C5', 'args': {'zone': 'a5', 'mode': 'b5'}},
            {'name': 'C6', 'args': {'zone': 'b6', 'mode': 'c6'}},
            {'name': 'C7', 'args': {'zone': 'c2', 'mode': 'd7'}},
            {'name': 'C8', 'args': {'zone': 'd8', 'mode': 'e8'}},
            {'name': 'C9', 'args': {'zone': 'e9', 'mode': 'a9'}},
        ]

    def test_case_1(self):
        self.true(Always(
        Implies(
            N('C2'),
            FreezeArg(
                'zone',
                Eventually(
                    Now(lambda e, c: name(c) == 'C7' and zone(c) == e['zone'])
                )
            )
        )
    ))


if __name__ == '__main__':
    unittest.main()