from __future__ import annotations

import random
from typing import Callable, Optional
from dotmap import DotMap
import pprint

#########
# Types #
#########

CommandName = str
Command = DotMap
Test = list[Command]
TestSuite = list[Test]

Index = int
FreezeId = int | str
Environment = DotMap
TestConstraint = Callable[[Environment, Test, Index], bool]
CommandConstraint = Callable[[Environment, Command], bool]


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
            test_suite.append([cmd.toDict() for cmd in test])
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


####################
# Main Constraint  #
####################

def apply_test_constraint(tc: TestConstraint, test: Test) -> bool:
    return tc(DotMap(), test, 0)


def test_constraints(test : Test, constraints: list[TestConstraint]) -> bool:
    for constraint in constraints:
        if not apply_test_constraint(constraint, test):
            return False
    return True


#######################
# Auxiliary functions #
#######################

def last_satisfying_index(env: Environment, test: Test, cc: CommandConstraint) -> Optional[int]:
    indices = [i for i, cmd in enumerate(test) if cc(env, cmd)]
    return indices[-1] if indices else None


def first_satisfying_index(env: Environment, test: Test, cc: CommandConstraint) -> Optional[int]:
    indices = [i for i, cmd in enumerate(test) if cc(env, cmd)]
    return indices[0] if indices else None


def within(index: int, test: Test) -> bool:
    return 0 <= index < len(test)


pp = pprint.PrettyPrinter(indent=4,sort_dicts=False).pprint


######################
# Temporal operators #
######################


# --- Standard Logic ---

T: TestConstraint = lambda env, test, index: True
F: TestConstraint = lambda env, test, index: False  # Alternative semantics: Not(T)


def N(name: str) -> TestConstraint:
    return Now(Cmd(name))


def Cmd(name: str) -> CommandConstraint:
    """
    name
    """
    return lambda e,c: c['name'] == name


def Now(cc: CommandConstraint) -> TestConstraint:
    """
    cc
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return cc(env, test[index])
        else:
            return False
    return constraint


def Not(tc: TestConstraint) -> TestConstraint:
    """
    !tc
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        return not tc(env, test, index)
    return constraint


def And(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 & tc2
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        return tc1(env, test, index) and tc2(env, test, index)
    return constraint


def Or(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 | tc2
    Alternative semantics: Not(And(Not(tc1), Not(tc2)))
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        return tc1(env, test, index) or tc2(env, test, index)
    return constraint


def Implies(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 -> tc2
    """
    return Or(Not(tc1), tc2)


# --- Future Time Temporal Logic ---

def Next(tc: TestConstraint) -> TestConstraint:
    """
    ()tc
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index + 1, test):
            return tc(env, test, index + 1)
        else:
            return False
    return constraint


def Until(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 U tc2
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return tc2(env, test, index) or (tc1(env, test, index) and constraint(env, test, index + 1))
        else:
            return False
    return constraint


def Eventually(tc: TestConstraint) -> TestConstraint:
    """
    <> tc
    Alternative semantics: Until(T, tc)
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return tc(env, test, index) or constraint(env, test, index + 1)
        else:
            return False
    return constraint


def Always(tc: TestConstraint) -> TestConstraint:
    """
    [] tc
    Alternative semantics: Not(Eventually(Not(tc)))
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return tc(env, test, index) and constraint(env, test, index + 1)
        else:
            return True
    return constraint


# --- Past Time Temporal Operators ---

def Previous(tc: TestConstraint) -> TestConstraint:
    """
    (*)tc
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index - 1, test):
            return tc(env, test, index - 1)
        else:
            return False
    return constraint


def Since(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 S tc2
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return tc2(env, test, index) or (tc1(env, test, index) and constraint(env, test, index - 1))
        else:
            return False
    return constraint


def Once(tc: TestConstraint) -> TestConstraint:
    """
    <*> tc
    Alternative semantics: Since(T, tc)
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return tc(env, test, index) or constraint(env, test, index - 1)
        else:
            return False
    return constraint


def Historically(tc: TestConstraint) -> TestConstraint:
    """
    [*] tc
    Alternative semantics: Not(Once(Not(tc)))
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return tc(env, test, index) and constraint(env, test, index - 1)
        else:
            return True
    return constraint


# --- Freeze Operators ---

def FreezeCmdAs(id: FreezeId, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test, index: int) -> bool:
        env[id] = test[index]
        return tc(env, test, index)
    return constraint


def FreezeVarAs(var: str, id: str, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test, index: int) -> bool:
        env[id] = test[index][var]
        return tc(env, test, index)
    return constraint


def FreezeVar(var: str, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test, index: int) -> bool:
        env[var] = test[index][var]
        return tc(env, test, index)
    return constraint


######################
# Constraint Library #
######################

def response(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    [](tc1 -> <>tc2)
    """
    return Always(Implies(tc1, Eventually(tc2)))


def contains_command_count(cc: CommandConstraint, low: int, high: int) -> TestConstraint:
    """
    low <= |cc| <= high
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        commands = [c for c in test if cc(env, c)]
        return low <= len(commands) <= high
    return constraint


def command_preceeds_command(cc1: CommandConstraint, cc2: CommandConstraint) -> TestConstraint:
    """
    [](cc2 -> <#>cc1)
    """
    def constraint(env: Environment, test: Test, index: int) -> bool:
        indexC1 = first_satisfying_index(env, test, cc1)
        indexC2 = first_satisfying_index(env, test, cc2)
        if indexC2 is not None:
            return indexC1 is not None and indexC1 < indexC2
        else:
            return True
    return constraint


def command_followed_by_command(cc1: CommandConstraint, cc2: CommandConstraint) -> TestConstraint:
    """
    [](cc1 -> <>cc2)
    """
    return Always(Implies(Now(cc1), Eventually(Now(cc2))))


def command_followed_by_command_without(cc1: CommandConstraint, cc2: CommandConstraint, cc3: CommandConstraint) -> TestConstraint:
    """
    [](cc1 -> !cc2 U cc3)
    """
    return Always(Implies(Now(cc1), Until(Not(Now(cc2)), Now(cc3))))

