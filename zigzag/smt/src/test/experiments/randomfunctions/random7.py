from z3 import *
import random

timeline = Function('timeline', IntSort(), IntSort())
solver = Solver()

# Generate test in parts, randomly fixing different parts of the test and solving incrementally
for t in range(100):
    # Randomly generate constraints for each time step and then add new constraints
    random_value = random.randint(0, 20)
    solver.add(timeline(t) == random_value)

    # Add additional constraints (e.g., ensuring one value > 10 in the sequence)
    if t % 10 == 0:  # Every 10th step, force one value to be greater than 10
        solver.add(timeline(t) > 10)

    if solver.check() == unsat:
        break

if solver.check() == sat:
    model = solver.model()
    print("Incremental solution:")
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {model.eval(timeline(t_val))}")
else:
    print("No solution found.")
