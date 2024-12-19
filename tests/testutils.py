
import unittest
from dotmap import DotMap

from src.fuzz.temporal_logic import *
def name(cmd: CommandDict) -> str:
    return cmd['name']


def zone(map: CommandDict | Environment) -> str:
    return map['zone']


def mode(map: CommandDict | Environment) -> str:
    return map['mode']


def mk_test(*dict) -> Test:
    return [DotMap(cmd) for cmd in dict]


class BaseTestSuite(unittest.TestCase):

    def equal(self, tc: Constraint, result: bool):
        self.assertEqual(apply_constraint(self.test, tc), result)

    def true(self, tc: Constraint):
        self.equal(tc, True)

    def false(self, tc: Constraint):
        self.equal(tc, False)

