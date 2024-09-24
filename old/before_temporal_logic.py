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

def last_satisfying_index(test: Test, cc: CommandConstraint) -> Optional[int]:
    indices = [i for i, x in enumerate(test) if cc(x)]
    return indices[-1] if indices else None


def first_satisfying_index(test: Test, cc: CommandConstraint) -> Optional[int]:
    indices = [i for i, x in enumerate(test) if cc(x)]
    return indices[0] if indices else None


def cmd(name: str) -> CommandConstraint:
    return lambda c: c[0] == name


pp = pprint.PrettyPrinter(indent=4).pprint


######################
# Temporal operators #
######################

def notuntil(cc1: CommandConstraint, cc2: CommandConstraint) -> TestConstraint:
    """
    !cc1 U cc2
    """
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                return cc2(cmd) or ((not cc1(cmd)) and constraint(test_))
            case []:
                return False
    return constraint


def response(cc: CommandConstraint, tc: TestConstraint) -> TestConstraint:
    """
    [](cc -> ()tc)
    """
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                return (not cc(cmd) or tc(test_)) and constraint(test_)
            case []:
                return True
    return constraint


def always(tc: TestConstraint) -> TestConstraint:
    """
    []tc
    """
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(test) and constraint(test_)
            case []:
                return True
    return constraint


def eventually(cc: CommandConstraint) -> TestConstraint:
    """
    <>cc
    """
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                return cc(cmd) or constraint(test_)
            case []:
                return False
    return constraint


def implies(cc: CommandConstraint, tc: TestConstraint) -> TestConstraint:
    """
    cc -> tc
    """
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                return not cc(cmd) or tc(test_)
            case []:
                return True
    return constraint


# ====

true2: TestConstraint = lambda test: True
false2: TestConstraint = lambda test: False
# Rewrites to: not2(true2)


def cmd2(cc: CommandConstraint) -> TestConstraint:
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, _]:
                return cc(cmd)
            case []:
                return False
    return constraint


def not2(tc: TestConstraint) -> TestConstraint:
    """
    !tc
    """
    def constraint(test: Test) -> bool:
        return not(tc(test))
    return constraint


def and2(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 & tc2
    """
    def constraint(test: Test) -> bool:
        return tc1(test) and tc2(test)
    return constraint


def or2(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 | tc2
    Rewrites to: not2(and2(not2(tc1), not2(tc2)))
    """
    def constraint(test: Test) -> bool:
        return tc1(test) or tc2(test)
    return constraint


def implies2(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 -> tc2
    """
    return or2(not2(tc1), tc2)


def next2(tc: TestConstraint) -> TestConstraint:
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(test_)
            case []:
                return False
    return constraint


def until2(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 U tc2
    """
    or2(tc2, and2(tc1,next2(until(tc1, tc2))))


def eventually2(tc: TestConstraint) -> TestConstraint:
    """
    <> tc
    Rewrites to: until2(true2, tc)
    """
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(test) or tc(test_)
            case []:
                return False
    return constraint


def always2(tc: TestConstraint) -> TestConstraint:
    """
    [] tc
    Rewrites to: not2(eventually(not2(tc)))
    """
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(test) and tc(test_)
            case []:
                return True
    return constraint

# ====


######################
# Constraint Library #
######################

def contains_command_count(cc: CommandConstraint, low: int, high: int) -> TestConstraint:
    """
    low <= |cc| <= high
    """
    def constraint(test: Test) -> bool:
        commands = [c for c in test if cc(c)]
        return low <= len(commands) <= high
    return constraint


def command_preceeds_command(cc1: CommandConstraint, cc2: CommandConstraint) -> TestConstraint:
    """
    [](cc2 -> <#>cc1)
    """
    def constraint(test: Test) -> bool:
        indexC1 = first_satisfying_index(test, cc1)
        indexC2 = first_satisfying_index(test, cc2)
        if indexC2 is not None:
            return indexC1 is not None and indexC1 < indexC2
        else:
            return True
    return constraint


def command_followed_by_command(cc1: CommandConstraint, cc2: CommandConstraint) -> TestConstraint:
    """
    [](cc1 -> <>cc2)
    """
    def constraint(test: Test) -> bool:
        indexC1 = last_satisfying_index(test, cc1)
        indexC2 = last_satisfying_index(test, cc2)
        if indexC1 is not None:
            return indexC2 is not None and indexC1 < indexC2
        else:
            return True
    return constraint


def command_followed_by_command_without(cc1: CommandConstraint, cc2: CommandConstraint, cc3: CommandConstraint) -> TestConstraint:
    """
    [](cc1 -> !cc2 U cc3)
    """
    def constraint(test: Test) -> bool:
        return response(cc1, notuntil(cc2, cc3))(test)
    return constraint

