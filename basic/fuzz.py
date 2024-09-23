

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
CommandConstraintOrString = CommandConstraint | str


########################
# Generation Functions #
########################

def generate_tests(cmdDict: dict, enumDict: dict, test_constraint: TestConstraint, nr_tests: int, nr_cmds: int) -> TestSuite:
    test_suite: TestSuite = []
    count: int = 0
    while count != nr_tests:
        test = generate_test(cmdDict, enumDict, nr_cmds)
        if test_constraint(test) and test not in test_suite:
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

def test_constraint(test : Test) -> bool:
    constraints = [
      # contains_command_count('C5', 1, 2),
      # command_preceeds_command('C1', 'C2'),
      # command_followed_by_command('C3', 'C4'),
      # command_followed_by_command_without('C5', 'C6', 'C7')
      contains_command_count('TIME_CORR_REQUEST', 1, 1),
      contains_command_count('DDM_SET_DWN_TZ_CONFIG', 1, 1),
      command_preceeds_command('DDM_CLEAR_DWN_DP_BUFFER', 'DDM_SET_DWN_TZ_CONFIG'),
      command_followed_by_command('DDM_ENABLE_DWN_PB_ENTRY_GATE', 'DDM_ENABLE_DWN_PB_EXIT_GATE'),
    ]
    for constraint in constraints:
        if not constraint(test):
            return False
    return True


#######################
# Auxiliary functions #
#######################

def pred_of(cmd_contraint: CommandConstraintOrString) -> CommandConstraint:
    if type(cmd_contraint) == str:
        return lambda c: c[0] == cmd_contraint
    else:
        return cmd_contraint


def last_satisfying_index(test: Test, p: CommandConstraint) -> Optional[int]:
    indices = [i for i, x in enumerate(test) if p(x)]
    return indices[-1] if indices else None


def first_satisfying_index(test: Test, p: CommandConstraint) -> Optional[int]:
    indices = [i for i, x in enumerate(test) if p(x)]
    return indices[0] if indices else None


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

def contains_command_count(cmd_pred: CommandConstraintOrString, low: int, high: int) -> TestConstraint:
    # ... C1 ... C1 ...
    def constraint(test: Test) -> bool:
        pred: TestConstraint = pred_of(cmd_pred)
        commands = [c for c in test if pred(c)]
        return low <= len(commands) <= high
    return constraint


def command_preceeds_command(cmd_pred1: CommandConstraintOrString, cmd_pred2: CommandConstraintOrString) -> TestConstraint:
    # ... C1! ... C2? ...
    def constraint(test: Test) -> bool:
        pred1 = pred_of(cmd_pred1)
        pred2 = pred_of(cmd_pred2)
        indexC1 = first_satisfying_index(test, pred1)
        indexC2 = first_satisfying_index(test, pred2)
        if indexC2 is not None:
            return indexC1 is not None and indexC1 < indexC2
        else:
            return True
    return constraint


def command_followed_by_command(cmd_pred1: CommandConstraintOrString, cmd_pred2: CommandConstraintOrString) -> bool:
    # ... C1? ... C2! ...
    def constraint(test: Test) -> bool:
        pred1 = pred_of(cmd_pred1)
        pred2 = pred_of(cmd_pred2)
        indexC1 = last_satisfying_index(test, pred1)
        indexC2 = last_satisfying_index(test, pred2)
        if indexC1 is not None:
            return indexC2 is not None and indexC1 < indexC2
        else:
            return True
    return constraint


def command_followed_by_command_without(cmd_pred1: CommandConstraintOrString, cmd_pred2: CommandConstraintOrString, cmd_pred3: CommandConstraintOrString) -> bool:
    #  C1?   ...  C2!
    #  |__________|
    #     not C3
    def constraint(test: Test) -> bool:
        pred1 = pred_of(cmd_pred1)
        pred2 = pred_of(cmd_pred2)
        pred3 = pred_of(cmd_pred3)
        return response(pred1, until(pred3, pred2))(test)
    return constraint



