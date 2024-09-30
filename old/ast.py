from __future__ import annotations

import random
from typing import Callable, Optional
from dotmap import DotMap
from dataclasses import dataclass
import pprint

#########
# Types #
#########

Command = DotMap
Test = list[Command]
TestSuite = list[Test]
Environment = DotMap
FreezeId = int | str


########################
# Generation Functions #
########################

def generate_tests(cmdDict: dict, enumDict: dict, constraints: list[Constraint], nr_tests: int, nr_cmds: int) -> TestSuite:
    test_suite: TestSuite = []
    count: int = 0
    while count != nr_tests:
        test = generate_test(cmdDict, enumDict, nr_cmds)
        if test_constraints(test, constraints) and test not in test_suite:
            count += 1
            test_suite.append(test)
    return test_suite


def generate_test(cmdDict: dict, enumDict: dict, nr_cmds: int) -> Test:
    command_names = list(cmdDict.keys())
    test: Test = []
    for nr in range(nr_cmds):
        command: Command = DotMap()
        command_name = random.choice(command_names)
        command['name'] = command_name
        arg_types = cmdDict[command_name]['args']
        for arg_type in arg_types:
            name = arg_type['name']
            type = arg_type['type']
            if type == 'unsigned_arg':
                value = random.random()
            else:
                value = random.choice(enumDict[type])
            command[name] = value
        test.append(command)
    return test


########################
# Auxiliary functions  #
########################

def apply_constraint(tc: Constraint, test: Test) -> bool:
    return tc.evaluate(DotMap(), test, 0)


def test_constraints(test : Test, constraints: list[Constraint]) -> bool:
    for constraint in constraints:
        if not apply_constraint(constraint, test):
            return False
    return True


def within(index: int, test: Test) -> bool:
    return 0 <= index < len(test)


pp = pprint.PrettyPrinter(indent=4,sort_dicts=False).pprint


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
class T(Constraint):
    """Represents a constraint that always evaluates to True."""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return True


@dataclass
class F(Constraint):
    """Represents a constraint that always evaluates to False."""
    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return False


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
    condition: Callable[[Environment, Command], bool]
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


#####################
# Derived Functions #
#####################

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

@dataclass
class CountFuture(Constraint):
    constraint: Constraint
    min: int
    max: int
    """Counts the number of times in the future that the constraint holds"""

    def count(self, env: Environment, test: Test, index: int) -> int:
        if within(index, test):
            number = 1 if self.constraint.evaluate(env, test, index) else 0
            return number + self.count(env, test, index + 1)
        return 0

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        number = self.count(env, test, index)
        return self.min <= number <= self.max
