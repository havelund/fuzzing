import random
from typing import Callable, Optional
import pprint

#########
# Types #
#########

CommandName = str
Command = {'name': CommandName, 'args': dict[str, str]} # not a correct type
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
        args = {}
        arg_types = cmdDict[command_name]['args']
        for arg_type in arg_types:
            name = arg_type['name']
            type = arg_type['type']
            if type == 'unsigned_arg':
                value = random.random()
            else:
                value = random.choice(enumDict[type])
            args[name] = value
        command = {'name': command_name, 'args': args}
        test.append(command)
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


pp = pprint.PrettyPrinter(indent=4,sort_dicts=False).pprint


######################
# Temporal operators #
######################

T: TestConstraint = lambda test: True
F: TestConstraint = lambda test: False # Alternative semantics: Not(T)


def N(name: str) -> TestConstraint:
    return Now(Cmd(name))


def Cmd(name: str) -> CommandConstraint:
    """
    name
    """
    return lambda c: c['name'] == name


def Now(cc: CommandConstraint) -> TestConstraint:
    """
    cc
    """
    def constraint(test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                return cc(cmd)
            case []:
                return False
    return constraint


def Not(tc: TestConstraint) -> TestConstraint:
    """
    !tc
    """
    def constraint(test: Test) -> bool:
        return not tc(test)
    return constraint


def And(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 & tc2
    """
    def constraint(test: Test) -> bool:
        return tc1(test) and tc2(test)
    return constraint


def Or(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 | tc2
    Alternative semantics: Not(And(Not(tc1), Not(tc2)))
    """
    def constraint(test: Test) -> bool:
        return tc1(test) or tc2(test)
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
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(test_)
            case []:
                return False
    return constraint


# TODO:
def Until(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    """
    tc1 U tc2
    """
    # This does not work: Or(tc2, And(tc1, Next(Until(tc1, tc2))))
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc2(test) or (tc1(test) and constraint(test_))
            case []:
                return False
    return constraint


def Eventually(tc: TestConstraint) -> TestConstraint:
    """
    <> tc
    Alternative semantics: Until(T, tc)
    """
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(test) or constraint(test_)
            case []:
                return False
    return constraint


def Always(tc: TestConstraint) -> TestConstraint:
    """
    [] tc
    Alternative semantics: Not(Eventually(Not(tc)))
    """
    def constraint(test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(test) and constraint(test_)
            case []:
                return True
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
    return Always(Implies(Now(cc1), Eventually(Now(cc2))))


def command_followed_by_command_without(cc1: CommandConstraint, cc2: CommandConstraint, cc3: CommandConstraint) -> TestConstraint:
    """
    [](cc1 -> !cc2 U cc3)
    """
    return Always(Implies(Now(cc1), Until(Not(Now(cc2)), Now(cc3))))

