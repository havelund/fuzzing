
from abc import ABC
from typing import Dict, Any
from dataclasses import dataclass, is_dataclass, fields

import src.fuzz.utils as utils
from zigzag.smt.src.commands import *

Environment = Dict[str, Any]  # Environment maps strings to Z3 expressions (or ints)


def within(index: int, test: utils.Test) -> bool:
    """Checks whether an index is withing a test.

    :param index: the index.
    :param test: the test.
    :return: true iff the index is within the bounds of the test.
    """
    return 0 <= index < len(test)


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
class LTLConstraint(ASTNode,ABC):
    """Base class for all command parameter constraints."""
    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLVariableConstraint(LTLConstraint):
    """cmd(id=x)"""
    field: str
    value: str

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return getattr(Command, self.field)(timeline(t)) == env[self.value]


@dataclass
class LTLNumberConstraint(LTLConstraint):
    """cmd(id=42)"""
    field: str
    value: int

    def evaluate(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return getattr(Command, self.field)(timeline(t)) == self.value


@dataclass
class LTLFormula(ASTNode,ABC):
    """Base class for all formulas."""

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


