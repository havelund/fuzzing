
from fuzz import *
from dictionaries.dict_test1 import cmdDict, enumDict
# from dictionaries.dict_clipper1 import cmdDict, enumDict

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
    #tests = generate_tests(cmdDict, enumDict, constraints_test2, 10, 5)
    #pp(tests)

    test = [
        ('C1', [('zone', 'd1'), ('mode', 'e2')]),
        ('C2', [('zone', 'e3'), ('mode', 'a2')]),
        ('C3', [('zone', 'c2'), ('mode', 'd3')]),
        ('C4', [('zone', 'b2'), ('mode', 'c2')]),
        ('C5', [('zone', 'a2'), ('mode', 'b1')]),
        ('C6', [('zone', 'a2'), ('mode', 'b1')]),
        ('C7', [('zone', 'a2'), ('mode', 'b1')]),
        ('C8', [('zone', 'a2'), ('mode', 'b1')]),
        ('C9', [('zone', 'a2'), ('mode', 'b1')])
    ]

    testcases = [
        (1, Always(Implies(Now(Cmd('C1')), Eventually(Now(Cmd('C2'))))), True),
        (2, Not(Now(Cmd('C1'))), False),
        (3, Now(Cmd('C1')), True),
        (4, Always(Implies(Now(Cmd('C4')),Until(Not(Now(Cmd('C1'))),Now(Cmd('C9'))))), True)
    ]

    for i,f,r in testcases:
        assert f(test) == r, f"Test case {i} failed"




