from z3 import *

s = String('s')
a = Re("a")
# Instead of a.star(), use the global function Star(a)
regex = a + Star(a)  # This represents "a" concatenated with zero or more "a"s (i.e. one or more a's)

solver = Solver()
solver.add(InRe(s, regex))
#solver.add(s == "aaaa")  # For testing
print(solver.check())   # Expected: sat
print(solver.model())
