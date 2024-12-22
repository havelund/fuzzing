from z3 import *

# Define the string variable
s = String("s")

# Define the exact match string
exact_match = StringVal("abc")

# Create a solver instance
solver = Solver()

# Add the constraint that `s` must exactly match "abc"
# solver.add(s == exact_match)
solver.add(Or(s == "klaus", s == "arlene"))

# Solve the constraints
if solver.check() == sat:
    model = solver.model()
    print("s =", model[s].as_string())  # Get the concrete value of `s`
else:
    print("Unsatisfiable")


if __name__ == '__main__':
    pass

