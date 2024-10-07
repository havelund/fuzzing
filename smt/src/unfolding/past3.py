from z3 import *

# Define the command type: 0 = Move, 1 = Turn, 2 = Cancel
command_type = Function('command_type', IntSort(), IntSort())  # Track command type at each time step

# Define argument position timelines (arg1, arg2, ..., up to 10 positions if needed)
arg1 = Function('arg1', IntSort(), IntSort())  # Argument position 1 (e.g., speed, angle, etc.)
arg2 = Function('arg2', IntSort(), IntSort())  # Argument position 2, if needed
# Additional arguments can be added as needed

# Create an SMT solver
solver = Solver()

# Define the finite trace length
trace_length = 100

# Add constraints based on the command type and interpretation of argument positions
for t in range(trace_length):
    # If the command is Move (command_type == 0), interpret arg1 as speed
    solver.add(Implies(command_type(t) == 0, arg1(t) >= 0))  # Move command with non-negative speed

    # If the command is Turn (command_type == 1), interpret arg1 as angle
    solver.add(Implies(command_type(t) == 1, And(arg1(t) >= 0, arg1(t) <= 360)))  # Turn command with valid angle

    # If the command is Cancel (command_type == 2), no arguments are relevant
    solver.add(Implies(command_type(t) == 2, True))  # Cancel command has no arguments

# Add a specific constraint for time step 8 (e.g., Move with speed 0 at time step 8)
solver.add(And(command_type(8) == 0, arg1(8) == 0))  # Move command with speed 0 at time step 8

# Unfold the "always" condition across all time steps
for t in range(1, trace_length):
    # Check if at time step t, there is a Move command with speed == 0
    move_with_speed_zero = And(command_type(t) == 0, arg1(t) == 0)

    # Look back in the past for a Turn command with angle == 180
    # Make sure that there is no Cancel command between the Turn and the Move
    past_condition = Or([
        And(
            # There is a Turn command with angle == 180 at time step t_prime
            command_type(t_prime) == 1, arg1(t_prime) == 180,
            # Between t_prime and t, there is no Cancel command
            And([command_type(t_between) != 2 for t_between in range(t_prime + 1, t)])
        )
        for t_prime in range(t)  # Look back at all previous time steps
    ])

    # Add the constraint: If Move(speed=0) is observed, there must be a Turn(angle=180) in the past with no Cancel in between
    solver.add(Implies(move_with_speed_zero, past_condition))

# Add a constraint that Turn(angle == 180) cannot appear consecutively more than once
for t in range(1, trace_length):
    solver.add(Implies(command_type(t) == 1, Not(command_type(t - 1) == 1)))  # No consecutive Turn(angle=180)

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    # Inspect the values of the timeline at specific time steps
    for t_val in range(10):
        cmd_type_val = model.eval(command_type(t_val))
        print(f"At time {t_val}: command_type = {cmd_type_val}")
        if cmd_type_val == 0:  # Move command
            print(f"  Move command with speed = {model.eval(arg1(t_val))}")
        elif cmd_type_val == 1:  # Turn command
            print(f"  Turn command with angle = {model.eval(arg1(t_val))}")  # Angle is in arg1 as well
        else:
            print(f"  Cancel command")
else:
    print("No solution found.")

if __name__ == '__main__':
    pass
