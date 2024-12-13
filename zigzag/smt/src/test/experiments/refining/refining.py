from z3 import *
import random

# Define the command datatype: Move(speed: Int), Turn(angle: Int), Cancel()
Command = Datatype('Command')
Command.declare('mk_move_cmd', ('move_speed', IntSort()))  # Move command has a speed argument
Command.declare('mk_turn_cmd', ('turn_angle', IntSort()))  # Turn command has an angle argument
Command.declare('mk_cancel_cmd')  # Cancel command has no arguments
Command = Command.create()

# Create a function to represent the timeline of commands
timeline = Function('timeline', IntSort(), Command)

# Create an SMT solver
solver = Solver()

# Define the finite trace length
trace_length = 100

# ----------------------------------
# Property:
# [](move(0) -> !cancel S turn(180))
# ==================================

# Unfold the "always" condition across all time steps
for t in range(1, trace_length):
    # Check if at time step t, there is a Move command with speed == 0
    move_with_speed_zero = And(Command.is_mk_move_cmd(timeline(t)), Command.move_speed(timeline(t)) == 0)

    # Look back in the past for a Turn command with angle == 180
    # Ensure that no Cancel command occurred between the Turn and the Move
    past_condition = Or([
        And(
            # There is a Turn command with angle == 180 at time step t_prime
            Command.is_mk_turn_cmd(timeline(t_prime)), Command.turn_angle(timeline(t_prime)) == 180,
            # No Cancel command occurred between t_prime and t
            And([Not(Command.is_mk_cancel_cmd(timeline(t_between))) for t_between in range(t_prime + 1, t)])
        )
        for t_prime in range(t)  # Look back at all previous time steps
    ])

    # Add the constraint: If Move(speed=0), there must be a Turn(angle=180) in the past with no Cancel in between
    solver.add(Implies(move_with_speed_zero, past_condition))

# Add other constraints (optional)
# Ensure that every command at each time step is either Move, Turn, or Cancel
for t in range(trace_length):
    solver.add(Or(Command.is_mk_move_cmd(timeline(t)),
                  Command.is_mk_turn_cmd(timeline(t)),
                  Command.is_mk_cancel_cmd(timeline(t))))

# Add a specific constraint that at time step 8, the command is Move with speed == 0
solver.add(And(Command.is_mk_move_cmd(timeline(8)), Command.move_speed(timeline(8)) == 0))

# Solve and extract the model
if solver.check() == sat:
    model = solver.model()
    print("Original Solution:")

    # Store the original solution values
    solution = [model.eval(timeline(t)) for t in range(trace_length)]

    # Display original solution for the first few steps
    for t_val in range(10):
        cmd = solution[t_val]
        if model.eval(Command.is_mk_move_cmd(cmd)):
            print(f"At time {t_val}: Move command with speed = {model.eval(Command.move_speed(cmd))}")
        elif model.eval(Command.is_mk_turn_cmd(cmd)):
            print(f"At time {t_val}: Turn command with angle = {model.eval(Command.turn_angle(cmd))}")
        elif model.eval(Command.is_mk_cancel_cmd(cmd)):
            print(f"At time {t_val}: Cancel command")

    # --- refine solution ---

    # Start with explicitly protected steps
    critical_steps = {8}  # Protect step 8 where Move(speed=0) is enforced

    # Perform sensitivity analysis on the model
    for i in range(trace_length):
        if i in critical_steps:
            continue  # Skip already protected steps

        solver.push()  # Save the current solver state

        # Randomize the i-th value (must still be valid: Move, Turn, or Cancel)
        random_choice = random.choice(['move', 'turn', 'cancel'])
        if random_choice == 'move':
            solver.add(timeline(i) == Command.mk_move_cmd(random.randint(0, 20)))
        elif random_choice == 'turn':
            solver.add(timeline(i) == Command.mk_turn_cmd(random.randint(0, 360)))
        else:
            solver.add(timeline(i) == Command.mk_cancel_cmd)

        # Check satisfiability
        if solver.check() != sat:
            critical_steps.add(i)  # Mark step as critical

        solver.pop()  # Restore the solver to the state before randomization

    # Randomize non-critical steps
    for i in range(trace_length):
        if i in critical_steps:
            continue  # Skip critical steps

        random_choice = random.choice(['move', 'turn', 'cancel'])
        if random_choice == 'move':
            solution[i] = Command.mk_move_cmd(random.randint(0, 20))
        elif random_choice == 'turn':
            solution[i] = Command.mk_turn_cmd(random.randint(0, 360))
        else:
            solution[i] = Command.mk_cancel_cmd

    # Display modified solution (Randomized non-critical steps)
    print("\nModified Solution (Randomized non-critical steps):")
    for t_val in range(10):
        cmd = solution[t_val]
        if model.eval(Command.is_mk_move_cmd(cmd)):
            print(f"At time {t_val}: Move command with speed = {model.eval(Command.move_speed(cmd))}")
        elif model.eval(Command.is_mk_turn_cmd(cmd)):
            print(f"At time {t_val}: Turn command with angle = {model.eval(Command.turn_angle(cmd))}")
        elif model.eval(Command.is_mk_cancel_cmd(cmd)):
            print(f"At time {t_val}: Cancel command")


if __name__ == '__main__':
    pass




