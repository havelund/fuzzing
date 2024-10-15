
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


#############
# Constants #
#############

class Constants:
    """
    Constants used in randomization, if not provided by user.
    """
    MIN_INTEGER = 0
    MAX_INTEGER = 1_000_000


class INDEX:
    """
    Constants for indexing pre-defined fields of dictionaries.
    """
    ARGS = 'args'
    ARGUMENT = 'argument'
    CMD_DICT = 'cmd_dict'
    COMMAND = 'command'
    COMMANDS = 'commands'
    CONSTRAINTS = 'constraints'
    ENUM_DICT = 'enum_dict'
    KIND = 'kind'
    NAME = 'name'
    RANGE_MAX = 'range_max'
    RANGE_MIN = 'range_min'
    TEST_SIZE = 'test_size'
    TESTSUITE_SIZE = 'testsuite_size'
    TYPE = 'type'


class VALUE:
    """
    Constants representing pre-defined contents of dictionaries.
    """
    INCLUDE = 'include'
    RANGE = 'range'
    UNSIGNED_ARG = 'unsigned_arg'


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