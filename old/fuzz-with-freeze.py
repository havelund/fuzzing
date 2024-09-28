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
Environment = dict[int, Command]
TestConstraint = Callable[[Environment, Test], bool]
CommandConstraint = Callable[[Environment, Command], bool]
FreezeId = int | str

test = [
    {'name': 'C0', 'args': {'zone': 'b1', 'mode': 'c3'}},
    {'name': 'C1', 'args': {'zone': 'c3', 'mode': 'd1'}},
    {'name': 'C2', 'args': {'zone': 'e1', 'mode': 'a2'}},
    {'name': 'C3', 'args': {'zone': 'c3', 'mode': 'd1'}},
    {'name': 'C4', 'args': {'zone': 'a3', 'mode': 'b3'}},
    {'name': 'C5', 'args': {'zone': 'a3', 'mode': 'b3'}},
    {'name': 'C6', 'args': {'zone': 'a3', 'mode': 'b3'}},
    {'name': 'C7', 'args': {'zone': 'e1', 'mode': 'b3'}},
    {'name': 'C8', 'args': {'zone': 'a3', 'mode': 'b3'}},
    {'name': 'C9', 'args': {'zone': 'a3', 'mode': 'b3'}},
    # -----
    {'name': 'C2', 'args': {'zone': 'e1', 'mode': 'a2'}},
    {'name': 'C6', 'args': {'zone': 'a3', 'mode': 'b3'}},
    {'name': 'C7', 'args': {'zone': 'e11', 'mode': 'b3'}},
]


def N(name: str) -> TestConstraint:
    return Now(Cmd(name))


def Cmd(name: str) -> CommandConstraint:
    return lambda e,c: c['name'] == name


def Now(cc: CommandConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [cmd, *test_]:
                return cc(env, cmd)
            case []:
                return False
    return constraint


def Not(tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        return not tc(env, test)
    return constraint


def And(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        return tc1(env, test) and tc2(env, test)
    return constraint


def Or(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        return tc1(env, test) or tc2(env, test)
    return constraint


def Implies(tc1: TestConstraint, tc2: TestConstraint) -> TestConstraint:
    return Or(Not(tc1), tc2)


def Always(tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(env, test) and constraint(env, test_)
            case []:
                return True
    return constraint


def Eventually(tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        match test:
            case [_, *test_]:
                return tc(env, test) or constraint(env, test_)
            case []:
                return False
    return constraint


def FreezeCmdAs(id: FreezeId, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        env[id] = test[0]
        return tc(env, test)
    return constraint


def FreezeArgAs(arg: str, id: str, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        env[id] = test[0]['args'][arg]
        return tc(env, test)
    return constraint


def FreezeArg(arg: str, tc: TestConstraint) -> TestConstraint:
    def constraint(env: Environment, test: Test) -> bool:
        env[arg] = test[0]['args'][arg]
        return tc(env, test)
    return constraint


def name(cmd: Command) -> str:
    return cmd['name']


def zone(cmd: Command) -> str:
    return cmd['args']['zone']


def mode(cmd: Command) -> str:
    return cmd['args']['mode']


if __name__ == '__main__':
    formula1 = Eventually(
        And(N('C2'),
            FreezeCmdAs(1,
                        Eventually(
                       Now(lambda e, c: name(c) == 'C7' and zone(c) == zone(e[1]))
                   ))))
    formula2 = Always(
        Implies(
            N('C2'),
            FreezeCmdAs(
                1,
                Eventually(
                    Now(lambda e, c: name(c) == 'C7' and zone(c) == zone(e[1]))
                )
            )
        )
    )
    formula3 = Always(
        Implies(
            N('C2'),
            FreezeArgAs(
                'zone', 'zone',
                Eventually(
                    Now(lambda e, c: name(c) == 'C7' and zone(c) == e['zone'])
                )
            )
        )
    )
    formula4 = Always(
        Implies(
            N('C2'),
            FreezeArg(
                'zone',
                Eventually(
                    Now(lambda e, c: name(c) == 'C7' and zone(c) == e['zone'])
                )
            )
        )
    )
    result1 = formula1({}, test)
    result2 = formula2({}, test)
    result3 = formula3({}, test)
    result4 = formula3({}, test)
    print(result1)
    print(result2)
    print(result3)
    print(result4)
