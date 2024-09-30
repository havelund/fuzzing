
"""
Run using simplified test directories.
"""

from basic.src.fuzz import *
from dictionaries.dict_test1 import cmdDict, enumDict


NAME = 'name'
ARGS = 'args'
ZONE = 'zone'
MODE = 'mode'


def C7_b1_or_b2_and_not_c3(env: Environment, cmd: Command) -> bool:
    return cmd.name == 'C7' and cmd.zone in {'b1', 'b2'} and cmd.mode != 'c3'


def C7_with_zone(zone: str) -> CommandConstraint:
    def constraint(env: Environment, cmd: Command) -> bool:
        return cmd.name == 'C7' and cmd.zone == zone
    return constraint


constraints1: list[Constraint] = [
    CountFuture(N('C5'), 1, 2),
    Precedes(N('C1'), N('C2')),
    FollowedBy(N('C3'), N('C4'))
]

constraints2: list[Constraint] = [
    Eventually(N('C1')),
    Always(Implies(N('C1'), Eventually(C(C7_b1_or_b2_and_not_c3)))),
    Always(Implies(N('C2'), Eventually(C(C7_with_zone('b2'))))),
    Always(Implies(N('C2'), Eventually(C(C7_with_zone('b2')))))
]


if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, constraints1, 10, 5)
    pp(tests)

