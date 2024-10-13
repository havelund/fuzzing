
from dataclasses import dataclass

from utils import *


#######################
# Auxiliary Functions #
#######################

def within(index: int, test: Test) -> bool:
    return 0 <= index < len(test)


################
# Base Classes #
################

@dataclass
class Constraint:
    """Base class for all constraints."""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        raise NotImplementedError


@dataclass
class UnaryConstraint(Constraint):
    """Represents a constraint with a single operand."""
    operand: Constraint


@dataclass
class BinaryConstraint(Constraint):
    """Represents a constraint with two operands."""
    left: Constraint
    right: Constraint


#######################
# Logical Constraints #
#######################

@dataclass
class TRUE(Constraint):
    """Represents a constraint that always evaluates to True."""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return True


TRUE = TRUE()  # Turn it into a singleton

@dataclass
class FALSE(Constraint):
    """Represents a constraint that always evaluates to False."""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return False


FALSE = FALSE()  # Turn it into a singleton

@dataclass
class N(Constraint):
    name: str
    """Represents predicate command name n"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            cmd = test[index]
            return cmd['name'] == self.name
        return False


@dataclass
class C(Constraint):
    condition: CommandConstraint
    """Represents command predicate p"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            cmd = test[index]
            return self.condition(env, cmd)
        return False


@dataclass
class Not(UnaryConstraint):
    """Represents logical negation: !φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return not self.operand.evaluate(env, test, index)


@dataclass
class And(BinaryConstraint):
    """Represents logical conjunction: φ ∧ ψ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.left.evaluate(env, test, index) and self.right.evaluate(env, test, index)


@dataclass
class Or(BinaryConstraint):
    """Represents logical disjunction: φ ∨ ψ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.left.evaluate(env, test, index) or self.right.evaluate(env, test, index)


@dataclass
class Implies(BinaryConstraint):
    """Represents logical implication: φ → ψ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return Or(Not(self.left), self.right).evaluate(env, test, index)


###########################
# Future Time Constraints #
###########################

@dataclass
class Next(UnaryConstraint):
    """Represents the 'Next' operator: X φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index + 1, test):
            return self.operand.evaluate(env, test, index + 1)
        return False


@dataclass
class WeakNext(UnaryConstraint):
    """Represents the 'WeakNext' operator: X_weak φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index + 1, test):
            return self.operand.evaluate(env, test, index + 1)
        return True


@dataclass
class Until(BinaryConstraint):
    """Represents the 'Until' operator: φ U ψ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.right.evaluate(env, test, index) or (
                self.left.evaluate(env, test, index) and self.evaluate(env, test, index + 1)
            )
        return False


@dataclass
class Eventually(UnaryConstraint):
    """Represents the 'Eventually' operator: <> φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.operand.evaluate(env, test, index) or self.evaluate(env, test, index + 1)
        return False


@dataclass
class Always(UnaryConstraint):
    """Represents the 'Always' operator: [] φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.operand.evaluate(env, test, index) and self.evaluate(env, test, index + 1)
        return True


#########################
# Past Time Constraints #
#########################

@dataclass
class Previous(UnaryConstraint):
    """Represents the 'Previous' operator: P φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index - 1, test):
            return self.operand.evaluate(env, test, index - 1)
        return False


@dataclass
class WeakPrevious(UnaryConstraint):
    """Represents the weak 'Previous' operator: P_weak φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index - 1, test):
            return self.operand.evaluate(env, test, index - 1)
        return True


@dataclass
class Since(BinaryConstraint):
    """Represents the 'Since' operator: φ S ψ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.right.evaluate(env, test, index) or (
                self.left.evaluate(env, test, index) and self.evaluate(env, test, index - 1)
            )
        return False


@dataclass
class Once(UnaryConstraint):
    """Represents the 'Once' operator: O φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.operand.evaluate(env, test, index) or self.evaluate(env, test, index - 1)
        return False


@dataclass
class Historically(UnaryConstraint):
    """Represents the 'Historically' operator: H φ"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.operand.evaluate(env, test, index) and self.evaluate(env, test, index - 1)
        return True


####################
# Freeze Operators #
####################

@dataclass
class FreezeCmdAs(Constraint):
    """Represents freezing the command at the current index as a variable in the environment."""
    freeze_id: FreezeId
    constraint: Constraint

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            env[self.freeze_id] = test[index]
            return self.constraint.evaluate(env, test, index)
        return False


@dataclass
class FreezeVarAs(Constraint):
    """Represents freezing a specific variable in a command as a variable in the environment."""
    var: str
    freeze_id: str
    constraint: Constraint

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            env[self.freeze_id] = test[index][self.var]
            return self.constraint.evaluate(env, test, index)
        return False


@dataclass
class FreezeVar(Constraint):
    """Represents freezing a variable in the environment."""
    var: str
    constraint: Constraint

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            env[self.var] = test[index][self.var]
            return self.constraint.evaluate(env, test, index)
        return False


######################
# Derived Constructs #
######################

@dataclass
class FollowedBy(BinaryConstraint):
    """Represents the response constraint: [](tc1 -> <>tc2)"""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        formula = Always(Implies(self.left, Eventually(self.right)))
        return formula.evaluate(env, test, index)


@dataclass
class Precedes(BinaryConstraint):
    """
    Represents the past time response constraint: [](tc1 -> P tc2)
    """
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        formula = Always(Implies(self.left, Once(self.right)))
        return formula.evaluate(env, test, index)


####################
# Other Constructs #
####################

@dataclass
class CountFuture(Constraint):
    constraint: Constraint
    min: int
    max: int
    """
    Verifies that the number of times a constraint holds in the future,
    including now, is within a lower and an upper bound.
    """

    def count(self, env: Environment, test: Test, index: int) -> int:
        if within(index, test):
            number = 1 if self.constraint.evaluate(env, test, index) else 0
            return number + self.count(env, test, index + 1)
        return 0

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        number = self.count(env, test, index)
        return self.min <= number <= self.max


@dataclass
class CounPast(Constraint):
    constraint: Constraint
    min: int
    max: int
    """
    Verifies that the number of times a constraint holds in the past,
    including now, is within a lower and an upper bound.
    """

    def count(self, env: Environment, test: Test, index: int) -> int:
        if within(index, test):
            number = 1 if self.constraint.evaluate(env, test, index) else 0
            return number + self.count(env, test, index - 1)
        return 0

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        number = self.count(env, test, index)
        return self.min <= number <= self.max


@dataclass
class Range(Constraint):
    cmd_name: str
    arg_name: str
    min: int
    max: int

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        formula = Always(Implies(N(self.cmd_name), C(lambda e,c: self.min <= c[self.arg_name] <= self.max)))
        return formula.evaluate(env, test, index)


#############
# Semantics #
#############

def apply_constraint(tc: Constraint, test: Test) -> bool:
    return tc.evaluate(DotMap(), test, 0)


def test_constraints(test : Test, constraints: list[Constraint]) -> bool:
    for constraint in constraints:
        if not apply_constraint(constraint, test):
            return False
    return True
