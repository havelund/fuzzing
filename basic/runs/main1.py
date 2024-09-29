
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


constraints1: list[TestConstraint] = [
    contains_command_count(Cmd('C5'), 1, 2),
    command_preceeds_command(Cmd('C1'), Cmd('C2')),
    command_followed_by_command(Cmd('C3'), Cmd('C4')),
    command_followed_by_command_without(Cmd('C5'), Cmd('C6'), Cmd('C7'))
]

constraints2: list[TestConstraint] = [
    Eventually(N('C1')),
    Always(Implies(N('C1'), Eventually(Now(C7_b1_or_b2_and_not_c3)))),
    Always(Implies(N('C2'), Eventually(Now(C7_with_zone('b2'))))),
    Always(Implies(N('C2'), Eventually(Now(C7_with_zone('b2')))))
]


if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, constraints1, 10, 5)
    pp(tests)

