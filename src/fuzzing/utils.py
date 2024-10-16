
import sys
from typing import Callable, List, Union
from dotmap import DotMap
import pprint


#########
# Types #
#########

Command = DotMap
Test = List[Command]
TestSuite = List[Test]
Environment = DotMap
FreezeId = Union[int, str]
CommandConstraint = Callable[[Environment, Command], bool]


#############
# Constants #
#############

class INDEX:
    """
    Constants for indexing pre-defined fields of dictionaries.
    """
    ACTIVE = 'active'
    ARGS = 'args'
    ARGUMENT = 'argument'
    CMD_DICT = 'cmd_dict'
    COMMAND = 'command'
    COMMANDS = 'commands'
    CONSTRAINTS = 'constraints'
    ENUM_DICT = 'enum_dict'
    KIND = 'kind'
    LENGTH = 'length'
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
    EXCLUDE = 'exclude'
    INCLUDE = 'include'
    RANGE = 'range'
    UNSIGNED_ARG = 'unsigned_arg'
    INTEGER_ARG = 'integer_arg'
    FLOAT_ARG = 'float_arg'
    VAR_STRING_ARG = 'var_string_arg'


#######################
# Auxiliary Functions #
#######################

def error(msg: str):
    """Prints an error message and terminates the program.

    :param msg: the error message.
    """
    print(f'*** error: {msg}')
    sys.exit("Program terminated abnormally!")


def lookup_dict(dictionary: dict, field: str) -> object:
    """Looks up a field in a dictionary. If it is not defined an error message is issued
    and the program terminates.

    :param dictionary: the dictionary to look up in.
    :param field: the field to look up.
    :return: the object pointed to by that field in the dictionary.
    """
    if field in dictionary:
        return dictionary[field]
    else:
        error(f"'{field}' is not a key in {dictionary}")


def limits_unsigned_int(bits: int):
    """Returns the minimum and maximum values for an unsigned integer of a given number of bits.

    :param bits: the number of bits used for representation.
    """
    min_value = 0
    max_value = 2**bits - 1
    return min_value, max_value


def limits_signed_int(bits: int):
    """Returns the minimum and maximum values for a signed integer of a given number of bits.

    :param bits: the number of bits used for representation.
    """
    min_value = -2**(bits - 1)
    max_value = 2**(bits - 1) - 1
    return min_value, max_value


def limits_floating_point(bits: int):
    """Returns the minimum and maximum values for a floating-point number of a given number of bits.

    :param bits: the number of bits used for representation.
    """
    sign_bits = 1
    # Estimating exponent and mantissa sizes based on IEEE-like format
    if bits == 32:
        exponent_bits = 8
    elif bits == 64:
        exponent_bits = 11
    else:
        exponent_bits = (bits - sign_bits) // 2  # Rough estimate for non-standard sizes
    mantissa_bits = bits - sign_bits - exponent_bits
    max_exponent = 2**(exponent_bits - 1) - 1
    min_exponent = -(2**(exponent_bits - 1) - 1)
    max_value = (2 - 2**(-mantissa_bits)) * 2**max_exponent
    min_value = -max_value
    # smallest_positive = 2**min_exponent
    return min_value, max_value


# pp = pprint.PrettyPrinter(indent=4,sort_dicts=False).pprint