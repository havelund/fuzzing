import random
from z3 import *

# Randomly initialize values for some parts of the test
timeline_random = [random.randint(0, 20) for _ in range(100)]

# Now use Z3 to ensure the random timeline satisfies the constraints
timeline = Function('timeline', IntSort(), IntSort())
solver = Solver()

# Add constraints, using the randomized values as the initial guess
for t in range(100):
    solver.add(timeline(t) == timeline_random[t])

# Add other required constraints, like "at least one value > 10"
solver.add(Or([timeline(t) > 10 for t in range(100)]))

# Check if the random timeline satisfies the constraints
if solver.check() == sat:
    model = solver.model()
    print("Solution based on random initial timeline:")
    for t_val in range(10):
        print(f"At time {t_val}: timeline = {model.eval(timeline(t_val))}")
else:
    print("No solution found.")
