from z3 import *
from typing import Callable, Dict, Any, Optional
from src.fuzz.utils import Command, Test

# Define the Environment type
Environment = Dict[str, Any]  # Environment maps strings to Z3 expressions (or ints)


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


class ExpressionConstraint(Constraint):
    """A generic constraint that evaluates an arbitrary expression on the environment and time point."""

    def __init__(self, expression_fn: Callable[[Environment, int], BoolRef]):
        self.expression_fn = expression_fn

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return self.expression_fn(env, t)  # The user-defined expression is evaluated here


# Boolean Operators for the Abstract Syntax

class TRUE(Constraint):
    """Represents a constraint that is True."""
    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return True


TRUE = TRUE()  # Turn it into a singleton


class FALSE(Constraint):
    """Represents a constraint that is False."""
    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return False


FALSE = FALSE()  # Turn it into a singleton


class LogicNot(Constraint):
    """LogicNot(φ): Logical negation !φ."""

    def __init__(self, subformula: Constraint):
        self.subformula = subformula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Not(self.subformula.evaluate(env, t, end_time))


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


# Temporal Operators (Future Time)

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


# Past-Time Temporal Operators

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
        return True


class Since(Constraint):
    """φ S ψ: ψ holds at some point in the past, and φ has held since that point."""

    def __init__(self, left: Constraint, right: Constraint):
        self.left = left  # φ
        self.right = right  # ψ

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([And(self.right.evaluate(env, t_prime, end_time),
                       And([self.left.evaluate(env, t_i, end_time) for t_i in range(t_prime + 1, t + 1)]))
                   for t_prime in range(0, t + 1)])


# # Define the command datatype: Move(speed: Int), Turn(angle: Int), Cancel()
# Command = Datatype('Command')
# Command.declare('mk_move_cmd', ('move_speed', IntSort()))  # Move command has a speed argument
# Command.declare('mk_turn_cmd', ('turn_angle', IntSort()))  # Turn command has an angle argument
# Command.declare('mk_cancel_cmd')  # Cancel command has no arguments
# Command = Command.create()
#
# # Create a function to represent the timeline of commands
# timeline = Function('timeline', IntSort(), Command)

# Create an SMT solver
solver = Solver()


def print_model(timeline: Function, end_time: int, model: ModelRef, fixed: set[int] = set()):
    print("===============")
    print("Solution found!")
    print("===============")
    for i in range(end_time):
        cmd = model.eval(timeline(i))
        fixed_text = '*' if i in fixed else ''
        print(f'{i:3}: {cmd} {fixed_text}')
    print("---------------")


def solve_formula(timeline: Function, end_time: int, critical_steps: set[int], formula: Constraint, solver: Solver) -> Optional[ModelRef]:
    solver.add(formula.evaluate({}, 0, end_time))
    if solver.check() == sat:
        model = solver.model()
        print_model(timeline, end_time, model, critical_steps)
        return model
    else:
        print("No solution found.")
        return None


def refine_solver(timeline: Function, end_time: int, critical_steps: set[int], generate_random_command: Callable[[], Datatype], solver: Solver) -> ModelRef:
    for i in range(end_time):
        if i in critical_steps:
            continue

        solver.push()

        command = generate_random_command()
        solver.add(timeline(i) == command)

        if solver.check() != sat:
            satisfied = False
            critical_steps.add(i)
        else:
            satisfied = True

        solver.pop()

        if satisfied:
            solver.add(timeline(i) == command)

    if solver.check() != sat:
        assert False, 'model not satisfiable as expected'
    refined_model = solver.model()
    print_model(timeline, end_time, refined_model, critical_steps)
    return refined_model


def generate_test_satisfying_formula(
      timeline: Function,
      end_time: int,
      critical_steps: set[int],
      formula: Constraint,
      generate_command: Callable[[], Datatype],
      extract_command:  Callable[[Datatype], Command],
      solver: Solver) -> Test:
    solve_formula(timeline, end_time, critical_steps, formula, solver)
    model = refine_solver(timeline, end_time, critical_steps, generate_command, solver)
    return [extract_command(model.eval(timeline(i)), model) for i in range(end_time)]
    return
