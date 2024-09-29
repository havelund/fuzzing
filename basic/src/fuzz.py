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

FreezeId = int | str
Environment = DotMap
TestConstraint = Callable[[Environment, Test], bool]
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
    return tc(DotMap(), test)


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


pp = pprint.PrettyPrinter(indent=4,sort_dicts=False).pprint


######################
# Temporal operators #
######################

T: TestConstraint = lambda env, test: True
F: TestConstraint = lambda env, test: False  # Alternative semantics: Not(T)


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
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                return cc(env, cmd)
            case []:
                return False
    return constraint


def Not(tc: TestConstraint) -> TestConstraint:
    """
    !tc
    """
    def constraint(env: Environment, test: Test) -> bool:
        return not tc(env, test)
    return constraint


def And(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 & tc2
    """
    def constraint(env: Environment, test: Test) -> bool:
        return tc1(env, test) and tc2(env, test)
    return constraint


def Or(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 | tc2
    Alternative semantics: Not(And(Not(tc1), Not(tc2)))
    """
    def constraint(env: Environment, test: Test) -> bool:
        return tc1(env, test) or tc2(env, test)
    return constraint


def Implies(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 -> tc2
    """
    return Or(Not(tc1), tc2)


def Next(tc: TestConstraint) -> TestConstraint:
    """
    ()tc
    """
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(env, test_)
            case []:
                return False
    return constraint


def Until(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 U tc2
    """
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc2(env, test) or (tc1(env, test) and constraint(env, test_))
            case []:
                return False
    return constraint


def Eventually(tc: TestConstraint) -> TestConstraint:
    """
    <> tc
    Alternative semantics: Until(T, tc)
    """
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(env, test) or constraint(env, test_)
            case []:
                return False
    return constraint


def Always(tc: TestConstraint) -> TestConstraint:
    """
    [] tc
    Alternative semantics: Not(Eventually(Not(tc)))
    """
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(env, test) and constraint(env, test_)
            case []:
                return True
    return constraint


def FreezeCmdAs(id: FreezeId, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        env[id] = test[0]
        return tc(env, test)
    return constraint


def FreezeVarAs(var: str, id: str, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        env[id] = test[0][var]
        return tc(env, test)
    return constraint


def FreezeVar(var: str, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        env[var] = test[0][var]
        return tc(env, test)
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
    def constraint(env: Environment, test: Test) -> bool:
        commands = [c for c in test if cc(env, c)]
        return low <= len(commands) <= high
    return constraint


def command_preceeds_command(cc1: CommandConstraint, cc2: CommandConstraint) -> TestConstraint:
    """
    [](cc2 -> <#>cc1)
    """
    def constraint(env: Environment, test: Test) -> bool:
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

