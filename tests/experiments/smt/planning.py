
from z3 import *

# The time variables that we want to find values for:

t0 = Int('t0')
t1 = Int('t1')
t2 = Int('t2')
t3 = Int('t3')
t4 = Int('t4')

# Creating an empty solver, which we will add constraints to:

solver = Solver()

# Constraint for node 0:

solver.add(t0 == 0)

# Constraint for node 1:

solver.add(And(10 <= t1-t0, t1-t0 <= 20))

# Constraints for node 2

# from t1:
solver.add(Or(
    And(30 <= t2-t1, t2-t1 <= 40),
    60 <= t2-t1
))

# from t3:
solver.add(And(10 <= t2-t3, t2-t3 <= 20))

# Constraints for node 4:

# from t3:
solver.add(Or(
    And(20 <= t4-t3, t4-t3 <= 30),
    And(40 <= t4-t3, t4-t3 <= 50)
))

# from t0:
solver.add(And(60 <= t4-t0, t4-t0 <= 70))

# Additional constraint of t2-t1:
# solver.add(t2-t1 <= 35)

# Solving:

if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    print(model)
else:
    print("No solution found.")

# This prints without the additional constraint:
# ----------------------------------------------
# Solution found:
# [t1 = 10, t4 = 70, t3 = 50, t2 = 70, t0 = 0]

# This prints WITH the additional constraint:
# -------------------------------------------
# Solution found:
# [t1 = 10, t4 = 60, t3 = 30, t2 = 40, t0 = 0]

# If we change the additional constraint to:
# solver.add(t2-t1 <= 25)
# It prints:
# ------------------------------------------
# No solution found.