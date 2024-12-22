from z3 import *
import random

# Create an SMT solver
solver = Solver()

# Define an integer timeline
timeline = Function('timeline', IntSort(), IntSort())

# Set a trace length of 100
trace_length = 100

# Randomize the constraint range (e.g., between 0 and a randomly generated upper bound)
for t in range(trace_length):
    upper_bound = random.randint(10, 30)  # Randomize the upper bound for this run
    solver.add(timeline(t) >= 0, timeline(t) <= upper_bound)

# Add a constraint that at least one value must be greater than 15
solver.add(Or([timeline(t) > 15 for t in range(trace_length)]))

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()
    print("Solution with random upper bounds:")
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {model.eval(timeline(t_val))}")
else:
    print("No solution found.")
