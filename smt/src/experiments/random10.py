
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

    # Now, we perform a sensitivity analysis:
    # Check which values are critical to satisfying the constraints
    important_values = []
    non_important_values = []

    for i in range(trace_length):
        # Create a temporary solver to test changing each value
        temp_solver = Solver()

        # Add all values except the current one (i) and change it randomly
        for t in range(trace_length):
            if t != i:
                temp_solver.add(timeline(t) == solution[t])
            else:
                # Randomize the i-th value
                temp_solver.add(timeline(t) == random.randint(0, 20))

        # Add the key constraint again
        temp_solver.add(Or([timeline(t) > 10 for t in range(trace_length)]))

        # Check if the new solution is still valid
        if temp_solver.check() == sat:
            non_important_values.append(i)  # This value can be changed without breaking the solution
        else:
            important_values.append(i)  # This value is important and should not be changed

    # Display the result of the sensitivity analysis
    print("\nImportant values (should not be randomized):", important_values)
    print("Non-important values (can be randomized):", non_important_values)

    # Post-process: Randomize the non-important values
    for i in non_important_values:
        solution[i] = random.randint(0, 20)

    # Display the modified solution
    print("\nModified Solution (Randomized non-important values):")
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {solution[t_val]}")

else:
    print("No solution found.")
