
"""
Run using Europa Clipper directories.
"""

from basic.src.fuzz import *
from dictionaries.dict_clipper1 import cmdDict, enumDict

constraints1: list[Constraint] = [
    CountFuture(N('TIME_CORR_REQUEST'), 1, 1),
    CountFuture(N('DDM_SET_DWN_TZ_CONFIG'), 1, 1),
    Precedes(N('DDM_CLEAR_DWN_DP_BUFFER'), N('DDM_SET_DWN_TZ_CONFIG')),
    FollowedBy(N('DDM_ENABLE_DWN_PB_ENTRY_GATE'), N('DDM_ENABLE_DWN_PB_EXIT_GATE')),
]

if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, constraints1, 10, 5)
    pp(tests)
