
import unittest
from basic.src.fuzz import *
from dotmap import DotMap

def name(cmd: Command) -> str:
    return cmd['name']


def zone(map: Command | Environment) -> str:
    return map['zone']


def mode(map: Command | Environment) -> str:
    return map['mode']


def mk_test(*dict) -> Test:
    return [DotMap(cmd) for cmd in dict]


class BaseTestSuite(unittest.TestCase):

    def equal(self, tc: Constraint, result: bool):
        self.assertEqual(apply_constraint(tc, self.test), result)

    def true(self, tc: Constraint):
        self.equal(tc, True)

    def false(self, tc: Constraint):
        self.equal(tc, False)

