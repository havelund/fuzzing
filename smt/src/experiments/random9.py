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

# Let Z3 find the initial solution
if solver.check() == sat:
    model = solver.model()
    print("Original Solution:")

    # Store the original solution values
    solution = [model.eval(timeline(t)).as_long() for t in range(trace_length)]

    # Display original solution
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {solution[t_val]}")

    # Post-process: Randomize some of the values, while keeping them valid (0 <= value <= 20)
    for i in range(0, trace_length, 5):  # Randomize every 5th value
        solution[i] = random.randint(0, 20)

    # Display the modified solution
    print("\nModified Solution (Randomized some values):")
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {solution[t_val]}")

    # (Optional) You can now re-verify if the modified solution still satisfies constraints
    solver = Solver()  # Create a new solver
    for t in range(trace_length):
        solver.add(timeline(t) == solution[t])
    solver.add(Or([timeline(t) > 10 for t in range(trace_length)]))  # Re-apply key constraints

    if solver.check() == sat:
        print("\nModified solution is still valid!")
    else:
        print("\nModified solution does not satisfy constraints!")
else:
    print("No solution found.")
