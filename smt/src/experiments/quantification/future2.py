from z3 import *

# Define symbolic variables
t = Int('t')
x = Int('x')
command_name = Function('command_name', IntSort(), IntSort())
command_speed = Function('command_speed', IntSort(), IntSort())

solver = Solver()

# Universal constraint: commands must either be Move (1) or Turn (2), and speed must be non-negative
solver.add(ForAll(t, Implies(Or(command_name(t) == 1, command_name(t) == 2), command_speed(t) >= 0)))

# Existential constraint for uniqueness, but limit the range for existential quantifiers
# Here, we use manual instantiation by checking command_name for a limited range of t
for t_val in range(100):
    solver.add(Exists([x], And(command_name(t_val) == x,
                               Not(Exists([t], And(t != t_val, command_name(t) == x))))))

# Check if the constraints are satisfiable
if solver.check() == sat:
    print("Solution found:")
else:
    print("No solution found.")

if __name__ == '__main__':
    pass