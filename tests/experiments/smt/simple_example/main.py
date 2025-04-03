
from z3 import *

x, y, z = Ints('x y z')

s = Solver()

s.add(x + y + z == 42)
s.add(x < y, y < z)
s.add(x * z == y * y)

if s.check() == sat:
    print("SAT! One solution:")
    print(s.model())
else:
    print("unsat or unknown")
