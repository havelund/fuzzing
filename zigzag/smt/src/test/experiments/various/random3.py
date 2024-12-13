from z3 import *

# Define integer timeline
timeline = Function('timeline', IntSort(), IntSort())

# Create a solver instance
solver = Solver()

# Define the finite trace length
trace_length = 100

# Add constraints (e.g., at least one value in the timeline must be greater than 10)
solver.add(Or([timeline(t) > 10 for t in range(trace_length)]))

# Set other constraints (optional)
for t in range(trace_length):
    solver.add(timeline(t) >= 0, timeline(t) <= 20)

# Find multiple solutions
for i in range(5):  # Generate 5 different solutions
    if solver.check() == sat:
        model = solver.model()
        print(f"Solution {i + 1}:")
        for t_val in range(10):
            print(f"At time {t_val}: timeline = {model.eval(timeline(t_val))}")

        # Block the current solution
        solver.add(Or([timeline(t) != model.eval(timeline(t)) for t in range(trace_length)]))
    else:
        print("No more solutions.")
        break
