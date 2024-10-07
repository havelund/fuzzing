
"""
Run using Europa Clipper directories.
"""

"""
Requirement:
You generated {'name': 'DDM_SET_DWN_TZ_CONFIG', 'dwn_rate': 0.4349376742660054},
I was thinking about it and that would set the downlink rate to .434 bits per second. 
This would be reallllllly slow (although technically allowable). Can we make a constraint 
for a minimum value for an argument? Nominally we would set this rate to  between 25k to 2M
"""

from basic.src.fuzz import *
from dictionaries.dict_clipper1 import cmdDict, enumDict
import json

constraints1: list[Constraint] = [
    CountFuture(N('TIME_CORR_REQUEST'), 1, 1),
    CountFuture(N('DDM_SET_DWN_TZ_CONFIG'), 1, 1),
    Precedes(N('DDM_CLEAR_DWN_DP_BUFFER'), N('DDM_SET_DWN_TZ_CONFIG')),
    FollowedBy(N('DDM_ENABLE_DWN_PB_ENTRY_GATE'), N('DDM_ENABLE_DWN_PB_EXIT_GATE')),
    Range('DDM_SET_DWN_TZ_CONFIG', 'dwn_rate', 25_000, 2_000_000)
]

if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, constraints1, 10, 5)
    pp(tests)
    with open("testsuite.json", "w") as file:
        json.dump(tests, file, indent=4)
