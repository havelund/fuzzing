
"""
Run using simplified test directories.
"""

from basic.src.fuzz import *
from dictionaries.dict_test1 import cmdDict, enumDict


constraints1: list[TestConstraint] = [
    contains_command_count(Cmd('C5'), 1, 2),
    command_preceeds_command(Cmd('C1'), Cmd('C2')),
    command_followed_by_command(Cmd('C3'), Cmd('C4')),
    command_followed_by_command_without(Cmd('C5'), Cmd('C6'), Cmd('C7'))
]

constraints2: list[TestConstraint] = [
    Always(Implies(Now(Cmd('C1')), Eventually(Now(Cmd('C2')))))
]


if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, constraints2, 10, 5)
    pp(tests)

"""
    'C1': AB
    'C2': BC
    'C3': CD
    'C4': DE
    'C5': EA
    'C6': AB
    'C7': BC
    'C8': CD
    'C9': DE
    'C10': EA
"""