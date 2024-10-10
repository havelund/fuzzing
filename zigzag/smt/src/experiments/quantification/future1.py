from z3 import *

# Create symbolic variables for the command and its arguments at any time step
t = Int('t') # Symbolic variable representing time
t1 = Int('t1')
x = Int('x')
command_name = Function('command_name', IntSort(), IntSort())  # command_name is a function of time
command_speed = Function('command_speed', IntSort(), IntSort())  # command_speed is also a function of time

# Create an SMT solver
solver = Solver()

# Eventually (Move(speed > 10))
# The command 'Move' is represented as 1. We want to assert that at some time step t,
# the command is 'Move' and the speed is greater than 10.
eventually_move_fast = Exists(t, And(command_name(t) == 1, command_speed(t) > 10))
solver.add(eventually_move_fast)

# Add universal constraints for all time steps using ForAll
# For all t: the command must be either Move (1) or Turn (2), and speed must be non-negative
universal_constraints = ForAll(t, Implies(Or(command_name(t) == 1, command_name(t) == 2), command_speed(t) >= 0))
solver.add(universal_constraints)

# uniqueness_constraint = ForAll([t, t1],
#     Implies(And(t >= 0, t <= 100, t1 >= 0, t1 <= 100, t != t1), command_name(t) != command_name(t1)))



# uniqueness_constraint = ForAll(t,
#            ForAll(x,
#                   Implies(And(command_name(t) == x, t <= 100, t >= 0),
#                              Not(
#                                  Exists(t1,
#                                         And(t1 <= 100, t1 >= 0, t != t1, command_name(t1) == x))))))

uniqueness_constraint = ForAll(t,
                               Implies(
                                   And(0 <= t, t <= 100),
                                   ForAll(t1,
                                          Implies(
                                              And(0 <= t1, t1 <= 100, t != t1),
                                              command_name(t) != command_name(t1)

                                          ))))

solver.add(uniqueness_constraint)

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    # Optionally, inspect the values of command_name and command_speed at specific time steps
    for t_val in range(100):  # We can still inspect the solution at a finite number of time steps
        command_name_val = model.eval(command_name(t_val))
        command_speed_val = model.eval(command_speed(t_val))
        print(f"At time {t_val}: command_name = {command_name_val}, speed = {command_speed_val}")
else:
    print("No solution found.")


if __name__ == '__main__':
    pass
