import types
from abc import ABC
from typing import Callable, Dict, Any, Optional, Sequence, get_origin
from dataclasses import dataclass, is_dataclass, fields

from commands import *

Environment = Dict[str, Any]  # Environment maps strings to Z3 expressions (or ints)


@dataclass
class ASTNode(ABC):
    # Color codes
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

    def red(self, text: str) -> str:
        return f"{ASTNode.RED}{text}{ASTNode.RESET}"

    def blue(self, text: str) -> str:
        return f"{ASTNode.BLUE}{text}{ASTNode.RESET}"

    def green(self, text: str) -> str:
        return f"{ASTNode.GREEN}{text}{ASTNode.RESET}"

    def pretty_print(self, indent: int = 0) -> None:
        """Generic method to pretty print the dataclass instance with tree-like indentation."""
        TAB = 2
        indent_str = "|  " * indent
        cls_name = self.red(self.__class__.__name__)
        if is_dataclass(self) and fields(self):
            print(f"{indent_str}{cls_name}:")
        else:
            print(f"{indent_str}{cls_name}")
        if is_dataclass(self):
            for field in fields(self):
                value = getattr(self, field.name)
                field_name = self.blue(field.name)
                if isinstance(value, list):
                    print(f"{indent_str}|  {field_name}: [")
                    for item in value:
                        if isinstance(item, ASTNode):  # Nested ASTNode
                            item.pretty_print(indent + TAB + TAB)
                        else:
                            print(f"{indent_str}|    {self.green(item)}")  # Regular items
                    print(f"{indent_str}|  ]")
                elif isinstance(value, ASTNode):  # Nested ASTNode
                    print(f"{indent_str}|  {field_name}:")
                    value.pretty_print(indent + TAB)
                else:  # Other fields
                    print(f"{indent_str}|  {self.blue(field_name)}: {self.green(value)}")


@dataclass
class LTLConstraint(ASTNode):
    field: str
    value: str | int

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        assert isinstance(self.value, str | int)
        if isinstance(self.value, str):
            return getattr(Command, self.field)(timeline(t)) == env[self.value]
        else:
            return getattr(Command, self.field)(timeline(t)) == self.value


@dataclass
class LTLFormula(ASTNode,ABC):
    """Base class for all constraints."""

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLFreeze(LTLFormula):
    """Freeze a value at time t, bind it to a name, and apply it in a subformula."""
    name: str
    field: str
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        # Freeze the value at time t
        frozen_value = Int(f'frozen_{self.name}_{t}')
        env[self.name] = frozen_value
        # Add the freezing condition to the solver
        freeze_constraint = frozen_value == getattr(Command, self.field)(timeline(t))
        # Evaluate the subformula with the frozen value in the environment
        subformula_constraint = self.subformula.evaluate(env, t, end_time)
        return And(freeze_constraint, subformula_constraint)


@dataclass
class LTLPredicate(LTLFormula):
    """A generic constraint that evaluates an arbitrary expression on the environment and time point."""
    command_name: str
    constraints: list[LTLConstraint]

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        is_method: str = f'is_{self.command_name}'
        right_command: BoolRef = getattr(Command, is_method)(timeline(t))
        right_arguments: list[BoolRef] = [constraint.evaluate(env, t, end_time) for constraint in self.constraints]
        return And([right_command] + right_arguments)


@dataclass
class LTLTrue(LTLFormula):
    """Represents a constraint that is True."""

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return BoolVal(True)


LTLTRUE = LTLTrue()  # Turn it into a singleton


@dataclass
class LTLFalse(LTLFormula):
    """Represents a constraint that is False."""

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return BoolVal(False)


LTLFALSE = LTLFalse()  # Turn it into a singleton


@dataclass
class LTLNot(LTLFormula):
    """LogicNot(φ): Logical negation !φ."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Not(self.subformula.evaluate(env, t, end_time))


@dataclass
class LTLAnd(LTLFormula):
    """LogicAnd(φ, ψ): Logical conjunction (φ ∧ ψ)."""
    left: LTLFormula
    right: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And(self.left.evaluate(env, t, end_time), self.right.evaluate(env, t, end_time))


@dataclass
class LTLOr(LTLFormula):
    """LogicOr(φ, ψ): Logical disjunction (φ ∨ ψ)."""
    left: LTLFormula
    right: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or(self.left.evaluate(env, t, end_time), self.right.evaluate(env, t, end_time))


@dataclass
class LTLImplies(LTLFormula):
    """LogicImplies(φ → ψ): Logical implication (φ → ψ)."""
    left: LTLFormula
    right: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Implies(self.left.evaluate(env, t, end_time), self.right.evaluate(env, t, end_time))


@dataclass
class LTLEventually(LTLFormula):
    """Eventually φ: at some point in the future, φ holds."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(t, end_time)])


@dataclass
class LTLAlways(LTLFormula):
    """Always φ: at every point in the future, φ holds."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(t, end_time)])


@dataclass
class LTLNext(LTLFormula):
    """Next φ: in the next time step, φ holds."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.evaluate(env, t + 1, end_time)
        return BoolVal(False)


@dataclass
class LTLWeakNext(LTLFormula):
    """Weak Next φ: either φ holds in the next time step or the timeline ends."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.evaluate(env, t + 1, end_time)
        return BoolVal(True)  # If no next step, it's trivially true.


@dataclass
class LTLUntil(LTLFormula):
    """φ U ψ: φ holds until ψ holds at some point."""
    left: LTLFormula
    right: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([And(self.right.evaluate(env, t_prime, end_time),
                       And([self.left.evaluate(env, t_i, end_time) for t_i in range(t, t_prime)]))
                   for t_prime in range(t, end_time)])


@dataclass
class LTLOnce(LTLFormula):
    """Once φ: at some point in the past, φ held."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(0, t + 1)])


@dataclass
class LTLSofar(LTLFormula):
    """Historically φ: φ has always held in the past."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.evaluate(env, t_prime, end_time) for t_prime in range(0, t + 1)])


@dataclass
class LTLPrevious(LTLFormula):
    """Previous φ: φ holds at the previous time step."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.evaluate(env, t - 1, end_time)
        return BoolVal(False)


@dataclass
class LTLWeakPrevious(LTLFormula):
    """Weak Previous φ: either φ holds at the previous time step or it's the start of the timeline."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.evaluate(env, t - 1, end_time)
        return BoolVal(True)


@dataclass
class LTLSince(LTLFormula):
    """φ S ψ: ψ holds at some point in the past, and φ has held since that point."""
    left: LTLFormula
    right: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([And(self.right.evaluate(env, t_prime, end_time),
                       And([self.left.evaluate(env, t_i, end_time) for t_i in range(t_prime + 1, t + 1)]))
                   for t_prime in range(0, t + 1)])


@dataclass
class LTLParen(LTLFormula):
    """(φ): holds if φ holds."""
    subformula: LTLFormula

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return self.subformula.evaluate(env, t, end_time)


@dataclass
class LTLRule(ASTNode):
    """rule id: φ"""
    rule_name: str
    formula: LTLFormula

    def evaluate(self, end_time: int) -> BoolRef:
        return self.formula.evaluate({}, 0, end_time)


@dataclass
class LTLSpec(ASTNode):
    """collection of rules."""
    rules: list[LTLRule]

    def evaluate(self, end_time: int) -> BoolRef:
        smt_formulas: list[BoolRef] = [rule.evaluate(end_time) for rule in self.rules]
        return And(smt_formulas)


# Create an SMT solver
solver = Solver()


def print_model(timeline: Function, end_time: int, model: ModelRef, fixed: Optional[set[int]] = None):
    print("===============")
    print("Solution found!")
    print("===============")
    if fixed is None:
        fixed = set()
    for i in range(end_time):
        cmd = model.eval(timeline(i))
        fixed_text = '*' if i in fixed else ''
        print(f'{i:3}: {cmd} {fixed_text}')
    print("---------------")


def solve_formula(timeline: Function, end_time: int, critical_steps: set[int], formula: LTLFormula, solver: Solver) -> Optional[ModelRef]:
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
      formula: LTLFormula,
      generate_command: Callable[[], Datatype],
      extract_command:  Callable[[Datatype, ModelRef], utils.Command],
      solver: Solver) -> utils.Test:
    solve_formula(timeline, end_time, critical_steps, formula, solver)
    model = refine_solver(timeline, end_time, critical_steps, generate_command, solver)
    return [extract_command(model.eval(timeline(i)), model) for i in range(end_time)]
