from z3 import *
from typing import Callable, Dict

# Define the Environment type
Environment = Dict[str, Int]

# Abstract Syntax Classes for Temporal Logic

class Constraint:
    """Base class for all constraints."""
    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        raise NotImplementedError("Subclasses should implement this!")


class FreezeAsIn(Constraint):
    """Freeze a value at time t, bind it to a name, and apply it in a subformula."""
    def __init__(self, value_fn: Callable[[int], Int], name: str, subformula: Constraint):
        self.value_fn = value_fn  # Function to extract the value to freeze
        self.name = name  # Name to bind the frozen value to
        self.subformula = subformula  # Subformula that uses the frozen value

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        # Freeze the value at time t
        frozen_value = Int(f'frozen_{self.name}_{t}')
        env[self.name] = frozen_value
        # Add the freezing condition to the solver
        freeze_constraint = frozen_value == self.value_fn(t)
        # Evaluate the subformula with the frozen value in the environment
        subformula_constraint = self.subformula.evaluate(env, t, end_time)
        return And(freeze_constraint, subformula_constraint)


# Boolean Operators for the Abstract Syntax

class LogicAnd(Constraint):
    """LogicAnd(φ, ψ): Logical conjunction (φ ∧ ψ)."""
    def __init__(self, left: Constraint, right: Constraint):
        self.left = left
        self.right = right

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And(self.left.evaluate(env, t, end_time), self.right.evaluate(env, t, end_time))


class LogicOr(Constraint):
    """LogicOr(φ, ψ): Logical disjunction (φ ∨ ψ)."""
    def __init__(self, left: Constraint, right: Constraint):
        self.left = left
        self.right = right

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or(self.left.evaluate(env, t, end_time), self.right.evaluate(env, t, end_time))


class LogicImplies(Constraint):
    """LogicImplies(φ → ψ): Logical implication (φ → ψ)."""
    def __init__(self, left: Constraint, right: Constraint):
        self.left = left
        self.right = right

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Implies(self.left.evaluate(env, t, end_time), self.right.evaluate(env, t, end_time))


class Equal(Constraint):
    """Equal(x, y): x == y."""
    def __init__(self, x: Int, y: Int):
        self.x = x
        self.y = y

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return self.x == self.y


# Temporal Operators

class Eventually(Constraint):
    """Eventually φ: at some point in the future, φ holds."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(t, end_time)])


class Always(Constraint):
    """Always φ: at every point in the future, φ holds."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(t, end_time)])


class Next(Constraint):
    """Next φ: in the next time step, φ holds."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.evaluate(env, t + 1, end_time)
        return False


class WeakNext(Constraint):
    """Weak Next φ: either φ holds in the next time step or the timeline ends."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.evaluate(env, t + 1, end_time)
        return True  # If no next step, it's trivially true.


class Until(Constraint):
    """φ U ψ: φ holds until ψ holds at some point."""
    def __init__(self, left: Constraint, right: Constraint):
        self.left = left  # φ
        self.right = right  # ψ

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([And(self.right.evaluate(env, t_prime, end_time),
                       And([self.left.evaluate(env, t_i, end_time) for t_i in range(t, t_prime)]))
                   for t_prime in range(t, end_time)])


# Past-Time Operators

class Previous(Constraint):
    """Previous φ: φ holds at the previous time step."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.evaluate(env, t - 1, end_time)
        return False


class WeakPrevious(Constraint):
    """Weak Previous φ: either φ holds at the previous time step or it's the start of the timeline."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.evaluate(env, t - 1, end_time)
        return True  # If no previous step, it's trivially true.


class Since(Constraint):
    """φ S ψ: ψ holds at some point in the past, and φ has held since that point."""
    def __init__(self, left: Constraint, right: Constraint):
        self.left = left  # φ
        self.right = right  # ψ

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([And(self.right.evaluate(env, t_prime, end_time),
                       And([self.left.evaluate(env, t_i, end_time) for t_i in range(t_prime + 1, t + 1)]))
                   for t_prime in range(0, t + 1)])


class Once(Constraint):
    """Once φ: at some point in the past, φ held."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(0, t + 1)])


class Historically(Constraint):
    """Historically φ: φ has always held in the past."""
    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(0, t + 1)])


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

# Define the end time of the trace
end_time = 100

# Define an environment for binding frozen values
env: Environment = {}

# Example: Eventually, we see a Move command with the same speed as frozen at t=8
freeze_formula = FreezeAsIn(lambda t: Command.move_speed(timeline(t)), 'x',
                            Eventually(Equal(Int('x'), Command.move_speed(timeline(t)))))  # Now using Int('x') for comparison
formula = Always(freeze_formula)

# Add the Always constraint: always check the eventual condition
for t in range(0, end_time):
    solver.add(formula.evaluate(env, t, end_time))

# Solve and extract the model
if solver.check() == sat:
    model = solver.model()
    print("Solution found!")
    for t_val in range(10):
        cmd = model.eval(timeline(t_val))
        if model.eval(Command.is_mk_move_cmd(cmd)):
            print(f"At time {t_val}: Move command with speed = {model.eval(Command.move_speed(cmd))}")
        elif model.eval(Command.is_mk_turn_cmd(cmd)):
            print(f"At time {t_val}: Turn command with angle = {model.eval(Command.turn_angle(cmd))}")
        elif model.eval(Command.is_mk_cancel_cmd(cmd)):
            print(f"At time {t_val}: Cancel command")
else:
    print("No solution found.")



if __name__ == '__main__':
    pass