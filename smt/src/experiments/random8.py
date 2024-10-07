
from z3 import *
import random

# Define an integer timeline function
timeline = Function('timeline', IntSort(), IntSort())

# Create a solver instance
solver = Solver()

# Define the finite trace length
trace_length = 100

# Add basic constraints (e.g., values must be within a range)
for t in range(trace_length):
    solver.add(timeline(t) >= 0, timeline(t) <= 20)

# Add the constraint that at least one value must be greater than 10
solver.add(Or([timeline(t) > 10 for t in range(trace_length)]))

# Now progressively add random "hints" for some values (optional)
for t in range(0, trace_length, 10):  # Every 10th step, add some random "hints"
    random_value = random.randint(0, 20)
    # Instead of fixing the value exactly, let's give Z3 more freedom
    solver.add(timeline(t) == random_value)

# Check satisfiability and extract the model
if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    for t_val in range(10):  # Display the first 10 values in the solution
        print(f"At time {t_val}: timeline = {model.eval(timeline(t_val))}")
else:
    print("No solution found.")
