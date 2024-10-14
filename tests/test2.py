import unittest
from tests.testutils import *

class FuzzTestSuite2(BaseTestSuite):
    def setUp(self):
        self.test = mk_test(
            {'name': 'C0', 'zone': 'a0', 'mode': 'b0'},
            {'name': 'C1', 'zone': 'a5', 'mode': 'b8'},
            {'name': 'C2', 'zone': 'a2', 'mode': 'b6'},
            {'name': 'C3', 'zone': 'a3', 'mode': 'b3'},
            {'name': 'C4', 'zone': 'a4', 'mode': 'b4'},
            {'name': 'C5', 'zone': 'a5', 'mode': 'b5'},
            {'name': 'C6', 'zone': 'a6', 'mode': 'b6'},
            {'name': 'C7', 'zone': 'a2', 'mode': 'b7'},
            {'name': 'C8', 'zone': 'a8', 'mode': 'b8'},
            {'name': 'C9', 'zone': 'a2', 'mode': 'b6'}
        )

    def test_case_1(self):
        self.true(Always(
            Implies(
                N('C2'),
                FreezeVar(
                    'zone',
                    Eventually(
                        C(lambda e, c: name(c) == 'C7' and zone(c) == zone(e))
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
                                    C(lambda e, c: c.name == 'C9' and
                                                     c.zone == e.zone and
                                                     c.mode == e.mode)
                                )
                            )
                        )
                    )
                )
            )
        ))

    def test_case_3(self):
        self.true(Always(
            Implies(
                N('C8'),
                FreezeVar(
                    'mode',
                    Once(
                        And(
                            N('C5'),
                            FreezeVar(
                                'zone',
                                Once(
                                    C(lambda e, c: c.name == 'C1' and
                                                     c.zone == e.zone and
                                                     c.mode == e.mode)
                                )
                            )
                        )
                    )
                )
            )
        ))


if __name__ == '__main__':
    unittest.main()
