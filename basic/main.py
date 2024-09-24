
from fuzz import *
# from dictionaries.dict_test1 import cmdDict, enumDict
from dictionaries.dict_clipper1 import cmdDict, enumDict



constraints_test1: list[TestConstraint] = [
    contains_command_count(Cmd('C5'), 1, 2),
    command_preceeds_command(Cmd('C1'), Cmd('C2')),
    command_followed_by_command(Cmd('C3'), Cmd('C4')),
    command_followed_by_command_without(Cmd('C5'), Cmd('C6'), Cmd('C7'))
]

constraints_test2: list[TestConstraint] = [
    Always(Implies(Now(Cmd('C1')), Eventually(Now(Cmd('C2')))))
]

constraints_clipper1: list[TestConstraint] = [
    contains_command_count(Cmd('TIME_CORR_REQUEST'), 1, 1),
    contains_command_count(Cmd('DDM_SET_DWN_TZ_CONFIG'), 1, 1),
    command_preceeds_command(Cmd('DDM_CLEAR_DWN_DP_BUFFER'), Cmd('DDM_SET_DWN_TZ_CONFIG')),
    command_followed_by_command(Cmd('DDM_ENABLE_DWN_PB_ENTRY_GATE'), Cmd('DDM_ENABLE_DWN_PB_EXIT_GATE')),
]

if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, constraints_clipper1, 10, 5)
    pp(tests)
