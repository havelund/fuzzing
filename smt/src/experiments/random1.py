
from z3 import *

# Set a random seed for the solver
set_param('sat.random_seed', 420)

# Example: Define an integer timeline
timeline = Function('timeline', IntSort(), IntSort())

# Create a solver instance
solver = Solver()

# Define the finite trace length
trace_length = 100

# Add constraints (for example, at least one value in the timeline must be greater than 10)
solver.add(Or([timeline(t) > 10 for t in range(trace_length)]))

# Optionally, set other constraints (e.g., timeline values must be between 0 and 20)
for t in range(trace_length):
    solver.add(timeline(t) >= 0, timeline(t) <= 20)

# Check satisfiability and get the solution
if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {model.eval(timeline(t_val))}")
else:
    print("No solution found.")

