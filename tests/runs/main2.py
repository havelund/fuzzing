
"""
Run using Europa Clipper directories.
"""

import json

from src.fuzz.core import *
from data.input.clipper1.dict import cmdDict, enumDict


constraints1: list[Constraint] = [
    CountFuture(N('TIME_CORR_REQUEST'), 1, 1),
    CountFuture(N('DDM_SET_DWN_TZ_CONFIG'), 1, 1),
    Precedes(N('DDM_CLEAR_DWN_DP_BUFFER'), N('DDM_SET_DWN_TZ_CONFIG')),
    FollowedBy(N('DDM_ENABLE_DWN_PB_ENTRY_GATE'), N('DDM_ENABLE_DWN_PB_EXIT_GATE')),
    Range('DDM_SET_DWN_TZ_CONFIG', 'dwn_rate', 25_000, 2_000_000)
]

if __name__ == '__main__':
    tests = generate_testsuite(cmdDict, enumDict, constraints1, 10, 5)
    # pp(tests)
    print(tests)
    with open("testsuite.json", "w") as file:
        json.dump(tests, file, indent=4)
