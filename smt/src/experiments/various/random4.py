
import random
from z3 import *

# Define integer timeline
timeline = Function('timeline', IntSort(), IntSort())

# Create a solver instance
solver = Solver()

# Define the finite trace length
trace_length = 10

# Add a basic constraint (e.g., at least one value in the timeline must be greater than 10)
solver.add(Or([timeline(t) > 10 for t in range(trace_length)]))

# Add random constraints (optional)
for t in range(trace_length):
    rand_val = random.randint(0, 20)
    solver.add(timeline(t) >= 1, timeline(t) <= rand_val)

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()
    print("Solution found with random constraints:")
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {model.eval(timeline(t_val))}")
else:
    print("No solution found.")
