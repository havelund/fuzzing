from z3 import *

# Define the Move and Turn command datatypes
Move = Datatype('Move')
Move.declare('mk_move', ('speed', IntSort()))  # Move command has a speed argument
Move = Move.create()

Turn = Datatype('Turn')
Turn.declare('mk_turn', ('angle', IntSort()))  # Turn command has an angle argument
Turn = Turn.create()

# Define a disjoint union of Move and Turn commands
Command = Datatype('Command')
Command.declare('mk_move_cmd', ('move', Move))
Command.declare('mk_turn_cmd', ('turn', Turn))
Command = Command.create()

# Create functions to handle the timeline
timeline = Function('timeline', IntSort(), Command)

# Create an SMT solver
solver = Solver()

# Define the finite trace length
trace_length = 100

# Unfold the "always" condition across all time steps
for t in range(1, trace_length):
    # Check if at time step t, there is a Move command with speed == 0
    move_with_speed_zero = And(Command.is_mk_move_cmd(timeline(t)), Move.speed(Command.move(timeline(t))) == 0)

    # If there is such a Move command, look back in the past for a Turn command with angle == 180
    past_condition = Or(
        [And(Command.is_mk_turn_cmd(timeline(t_prime)), Turn.angle(Command.turn(timeline(t_prime))) == 180)
         for t_prime in range(t)])  # Look back at all previous time steps

    # Add the constraint: If Move(speed=0) is observed, there must be a Turn(angle=180) in the past
    solver.add(Implies(move_with_speed_zero, past_condition))

# Add other constraints (optional)
# For example, ensure that the command at each time step is either a Move or a Turn
for t in range(trace_length):
    solver.add(Or(Command.is_mk_move_cmd(timeline(t)), Command.is_mk_turn_cmd(timeline(t))))

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    # Inspect the values of the timeline at specific time steps
    for t_val in range(10):
        cmd = model.eval(timeline(t_val))  # Get the command at time t_val
        if model.eval(Command.is_mk_move_cmd(cmd)):  # Evaluate the is_mk_move_cmd condition
            print(f"At time {t_val}: Move command with speed = {model.eval(Move.speed(Command.move(cmd)))}")
        elif model.eval(Command.is_mk_turn_cmd(cmd)):  # Evaluate the is_mk_turn_cmd condition
            print(f"At time {t_val}: Turn command with angle = {model.eval(Turn.angle(Command.turn(cmd)))}")
else:
    print("No solution found.")

if __name__ == '__main__':
    pass