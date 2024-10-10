from z3 import *

# Create an array to store command names and speeds at different time steps
command_name_array = Array('command_name_array', IntSort(), IntSort())  # Array of command names
command_speed_array = Array('command_speed_array', IntSort(), IntSort())  # Array of speeds

# Create an SMT solver
solver = Solver()

# Eventually (Move(speed > 10))
# The command 'Move' is represented as 1. We want to assert that at some time step t,
# the command is 'Move' and the speed is greater than 10.
t = Int('t')
eventually_move_fast = Exists(t, And(Select(command_name_array, t) == 1, Select(command_speed_array, t) > 10))
solver.add(eventually_move_fast)

# Direct uniqueness check: avoid quantifiers and manually compare each time step pair
for t_val in range(100):
    for t1_val in range(t_val + 1, 100):
        solver.add(Select(command_name_array, t_val) != Select(command_name_array, t1_val))

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    # Inspect the values of the command name and speed at specific time steps
    for t_val in range(10):  # Show the first 10 time steps
        command_name_val = model.eval(Select(command_name_array, t_val))
        command_speed_val = model.eval(Select(command_speed_array, t_val))
        print(f"At time {t_val}: command_name = {command_name_val}, speed = {command_speed_val}")
else:
    print("No solution found.")


if __name__ == '__main__':
    pass
