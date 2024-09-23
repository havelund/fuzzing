

import random
from typing import Callable, Optional
import pprint

#########
# Types #
#########

CommandName = str
Command = tuple[CommandName, list[str]]
Test = list[Command]
TestSuite = list[Test]
TestConstraint = Callable[[Test], bool]
CommandConstraint = Callable[[Command], bool]


########################
# Generation Functions #
########################

def generate_tests(cmdDict: dict, enumDict: dict, constraints: list[TestConstraint], nr_tests: int, nr_cmds: int) -> TestSuite:
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
        command_name = random.choice(command_names)
        arg_types = cmdDict[command_name]['args']
        args = []
        for arg_type in arg_types:
            name = arg_type['name']
            type = arg_type['type']
            if type == 'unsigned_arg':
                value = random.random()
            else:
                values = enumDict[type]
                value = random.choice(values)
            args.append((name, value))
        test.append((command_name, args))
    return test


####################
# Main Constraint  #
####################

def test_constraints(test : Test, constraints: list[TestConstraint]) -> bool:
    for constraint in constraints:
        if not constraint(test):
            return False
    return True


#######################
# Auxiliary functions #
#######################

def last_satisfying_index(test: Test, p: CommandConstraint) -> Optional[int]:
    indices = [i for i, x in enumerate(test) if p(x)]
    return indices[-1] if indices else None


def first_satisfying_index(test: Test, p: CommandConstraint) -> Optional[int]:
    indices = [i for i, x in enumerate(test) if p(x)]
    return indices[0] if indices else None


def cmd(n: str) -> TestConstraint:
    return lambda c: c[0] == n


pp = pprint.PrettyPrinter(indent=4).pprint


######################
# Temporal operators #
######################

def until(p: CommandConstraint, q: CommandConstraint) -> TestConstraint:
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                q(cmd) or (p(cmd) and constraint(test_))
            case []:
                return False
    return constraint


def response(p: CommandConstraint, q: TestConstraint) -> TestConstraint:
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                not p(cmd) or q(test_)
            case []:
                return True
    return constraint


######################
# Constraint Library #
######################

def contains_command_count(cmd_pred: CommandConstraint, low: int, high: int) -> TestConstraint:
    # ... C1 ... C1 ...
    def constraint(test: Test) -> bool:
        commands = [c for c in test if cmd_pred(c)]
        return low <= len(commands) <= high
    return constraint


def command_preceeds_command(cmd_pred1: CommandConstraint, cmd_pred2: CommandConstraint) -> TestConstraint:
    # ... C1! ... C2? ...
    def constraint(test: Test) -> bool:
        indexC1 = first_satisfying_index(test, cmd_pred1)
        indexC2 = first_satisfying_index(test, cmd_pred2)
        if indexC2 is not None:
            return indexC1 is not None and indexC1 < indexC2
        else:
            return True
    return constraint


def command_followed_by_command(cmd_pred1: CommandConstraint, cmd_pred2: CommandConstraint) -> bool:
    # ... C1? ... C2! ...
    def constraint(test: Test) -> bool:
        indexC1 = last_satisfying_index(test, cmd_pred1)
        indexC2 = last_satisfying_index(test, cmd_pred2)
        if indexC1 is not None:
            return indexC2 is not None and indexC1 < indexC2
        else:
            return True
    return constraint


def command_followed_by_command_without(cmd_pred1: CommandConstraint, cmd_pred2: CommandConstraint, cmd_pred3: CommandConstraint) -> bool:
    #  C1?   ...  C2!
    #  |__________|
    #     not C3
    def constraint(test: Test) -> bool:
        return response(cmd_pred1, until(cmd_pred3, cmd_pred2))(test)
    return constraint



