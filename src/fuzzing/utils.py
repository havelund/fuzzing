
import sys
from typing import Callable
from dotmap import DotMap
import pprint


#########
# Types #
#########

Command = DotMap
Test = list[Command]
TestSuite = list[Test]
Environment = DotMap
FreezeId = int | str
CommandConstraint = Callable[[Environment, Command], bool]


#######################
# Auxiliary Functions #
#######################

def error(msg: str):
    print(f'*** error: {msg}')
    sys.exit("Program terminated abnormally!")


def lookup_dict(dictionary: dict, name: str) -> object:
    if name in dictionary:
        return dictionary[name]
    else:
        error(f"'{name}' is not a key in {dictionary}")

pp = pprint.PrettyPrinter(indent=4,sort_dicts=False).pprint