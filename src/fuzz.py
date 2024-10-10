from __future__ import annotations

import argparse
import random
from typing import Callable
from dotmap import DotMap
from dataclasses import dataclass
import pprint
import json

#########
# Types #
#########

Command = DotMap
Test = list[Command]
TestSuite = list[Test]
Environment = DotMap
FreezeId = int | str
CommandConstraint = Callable[[Environment, Command], bool]


########################
# Generation Functions #
########################

class ArgumentConstraints:
    def __init__(self, constraints: list[Constraint]):
        self.commands: dict[str, dict[str, tuple[int, int]]] = {}
        for constraint in constraints:
            match constraint:
                case Range(cmd_name, arg_name, min, max):
                    if cmd_name not in self.commands:
                        self.commands[cmd_name] = {}
                    self.commands[cmd_name][arg_name] = (min, max)

    def random(self, command: str, arg: str) -> int:
        if command in self.commands:
            arg_map = self.commands[command]
            if arg in arg_map:
                min, max = arg_map[arg]
                return random.randrange(min, max)
        return random.randint(0,1000000)


def generate_testsuite(cmdDict: dict, enumDict: dict, constraints: list[Constraint], nr_tests: int, nr_cmds: int) -> TestSuite:
    test_suite: TestSuite = []
    count: int = 0
    arg_constraints = ArgumentConstraints(constraints)
    while count != nr_tests:
        test = generate_test(cmdDict, enumDict, arg_constraints, nr_cmds)
        if test_constraints(test, constraints) and test not in test_suite:
            count += 1
            test_suite.append([cmd.toDict() for cmd in test])
        else:
            print(f"failed")
    return test_suite


def generate_test(cmdDict: dict, enumDict: dict, arg_constraints: ArgumentConstraints, nr_cmds: int) -> Test:
    command_names = list(cmdDict.keys())
    test: Test = []
    for nr in range(nr_cmds):
        command: Command = DotMap()
        command_name = random.choice(command_names)
        command['name'] = command_name
        arg_types = cmdDict[command_name]['args']
        for arg_type in arg_types:
            arg_name = arg_type['name']
            arg_type = arg_type['type']
            if arg_type == 'unsigned_arg':
                value = arg_constraints.random(command_name, arg_name)
            else:
                value = random.choice(enumDict[arg_type])
            command[arg_name] = value
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


################
# Main program #
################

def main(args = None):
    # Obtain names of input file and output file:
    parser = argparse.ArgumentParser(description="Test suite generator")
    parser.add_argument("dictionary_file", help="command and enum dictionaries as a json file")
    parser.add_argument("testsuite_file", help="test suite as a json file")
    parser.add_argument("testsuite_size", help="number of tests to include in test suite", type=int)
    parser.add_argument("test_size", help="number of commands to include in a test", type=int)
    parsed_args = parser.parse_args(args)
    cmd_enum_file = parsed_args.dictionary_file
    testsuite_file = parsed_args.testsuite_file
    testsuite_size = parsed_args.testsuite_size
    test_size = parsed_args.test_size
    print('Reading command and enum dictionaries from:')
    print(f'  {cmd_enum_file}')
    print('Writing test suite to:')
    print(f'  {testsuite_file}')
    print('Test suite size and test size')
    print(f'  {testsuite_size} {test_size}')

    # Read the command and enum json file:
    with open(cmd_enum_file, 'r') as file:
        cmd_enum_dictionaries = json.load(file)
    cmd_dict = cmd_enum_dictionaries['cmd_dict']
    enum_dict = cmd_enum_dictionaries['enum_dict']

    # Define default constraints (fixed for now):
    constraints: list[Constraint] = [
        Range('DDM_SET_DWN_TZ_CONFIG', 'dwn_rate', 25_000, 2_000_000)
    ]

    # Generate test suite and write it to a file:
    tests = generate_testsuite(cmd_dict, enum_dict, constraints, testsuite_size, test_size)
    with open(testsuite_file, "w") as file:
        json.dump(tests, file, indent=4)


if __name__ == '__main__':
    args = [
        '/Users/khavelun/Desktop/development/pycharmworkspace/fuzzing/data/cmd_enum_dicts.json',
        '/Users/khavelun/Desktop/development/pycharmworkspace/fuzzing/data/testsuite.json',
        '2',
        '3'
    ]
    main(args)

