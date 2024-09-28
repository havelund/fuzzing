
import unittest
from basic.src.fuzz import *


def name(cmd: Command) -> str:
    return cmd['name']


def zone(map: Command | Environment) -> str:
    return map['zone']


def mode(map: Command | Environment) -> str:
    return map['mode']


class BaseTestSuite(unittest.TestCase):

    def equal(self, tc: TestConstraint, result: bool):
        self.assertEqual(apply_test_constraint(tc, self.test), result)

    def true(self, tc: TestConstraint):
        self.equal(tc, True)

    def false(self, tc: TestConstraint):
        self.equal(tc, False)

