
from fuzz import *
from dictionaries.dict_clipper1 import cmdDict, enumDict

constraints_test1: list[TestConstraint] = [
    contains_command_count(cmd('C5'), 1, 2),
    command_preceeds_command(cmd('C1'), 'C2'),
    command_followed_by_command(cmd('C3'), cmd('C4')),
    command_followed_by_command_without(cmd('C5'), cmd('C6'), cmd('C7'))
]

constraints_clipper1: list[TestConstraint] = [
    contains_command_count(cmd('TIME_CORR_REQUEST'), 1, 1),
    contains_command_count(cmd('DDM_SET_DWN_TZ_CONFIG'), 1, 1),
    command_preceeds_command(cmd('DDM_CLEAR_DWN_DP_BUFFER'), cmd('DDM_SET_DWN_TZ_CONFIG')),
    command_followed_by_command(cmd('DDM_ENABLE_DWN_PB_ENTRY_GATE'), cmd('DDM_ENABLE_DWN_PB_EXIT_GATE')),
]

if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, constraints_clipper1, 10, 5)
    pp(tests)

