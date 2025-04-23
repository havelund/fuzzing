
"""
Various utilities used throughout.
"""

import sys
from typing import Callable, List, Union, Dict
from dotmap import DotMap

import z3
from fuzz.options import Options

# ======
# Colors
# ======

DEBUG_COLOR = "\033[93m"    # Yellow
INSPECT_COLOR = "\033[94m"  # Blue
RESET_COLOR = "\033[0m"

# =====
# Types
# =====

CommandDict = Dict[str, Union[int, float, str]]
Test = List[CommandDict]
TestSuite = List[Test]
Environment = DotMap
FreezeId = Union[int, str]
CommandConstraint = Callable[[Environment, CommandDict], bool]


# =========
# Constants
# =========

class INDEX:
    """
    Constants for indexing pre-defined fields of dictionaries.
    """
    ACTIVE = 'active'
    ARGS = 'args'
    ARG = 'arg'
    CMD_DICT = 'cmd_dict'
    CMD1 = 'cmd1'
    CMD2 = 'cmd2'
    CMD = 'cmd'
    CMDS = 'cmds'
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
    EVENTUALLY = 'eventually'
    FOLLOWED_BY = 'followed_by'
    FOLLOWED_BY_NEXT = 'followed_by_next'
    PRECEDES = 'precedes'
    PRECEDES_PREV = 'precedes_prev'
    INCLUDE = 'include'
    RANGE = 'range'
    UNSIGNED_ARG = 'unsigned_arg'
    INTEGER_ARG = 'integer_arg'
    FLOAT_ARG = 'float_arg'
    VAR_STRING_ARG = 'var_string_arg'


# ===================
# Auxiliary Functions
# ===================

def headline(text: str):
    """Prints a text surrounded by frame lines.

    :param text: the text to be printed.
    """
    length = len(text) + 1
    line = '=' * length
    print(line)
    print(f'{text}:')
    print(line)


def debug(level: int, msg: str):
    """Emits debugging information depending on level.

    Whether message is printed depends on `Options.DEBUG_LEVEL`.
    :param level: 1=minimum, 2=medium, 3=maximum
    :param msg: message to be printed
    """
    assert level in [1,2,3], f'wrong debugging level {level}'
    if Options.DEBUG_LEVEL >= level:
        print(f"{DEBUG_COLOR}[DEBUG] {msg} {RESET_COLOR}")


def inspect(msg: str, doit: bool = True, stop: bool = False):
    """Used for here and now debugging, prints a message.

    :param msg: message to be printed.
    :param doit: flag indicating whether to print debug message or not.
    :param stop: flag indicating whether to stop and let the user use enter key to continue
    """
    if doit:
        print(f"{INSPECT_COLOR}[DEBUG] {msg} {RESET_COLOR}")
        if stop:
            input('press RETURN to continue')


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


def is_datatype_instance(val: z3.ExprRef) -> bool:
    """Checks whether a Z3 value is a datatype value.

    :param val: the value to test.
    :return True iff it is a datatype value.
    """
    try:
        return val.sort().kind() == z3.Z3_DATATYPE_SORT
    except:
        return False


def convert_z3_value(value):
    """
    Converts a Z3 value to a Python-native type.
    Only supports integers, reals, and strings.

    :param value: The Z3 value to convert.
    :return: A Python-native type (int, float, str).
    :raises TypeError: If the value is not an integer, real, or string.
    """
    if z3.is_int_value(value):
        return value.as_long()
    elif z3.is_rational_value(value):
        return float(value.as_fraction())
    elif z3.is_string_value(value):
        return value.as_string()
    elif is_datatype_instance(value):
        return str(value)  # TODO not sure about this
    else:
        raise TypeError(f"Unsupported Z3 value type: {value}")


def unsigned_int_bounds(bits: int) -> tuple[int, int]:
    """
    Returns (min, max) bounds for an unsigned integer with the given number of bits.
    """
    return (0, 2**bits - 1)


def signed_int_bounds(bits: int) -> tuple[int, int]:
    """
    Returns (min, max) bounds for a signed integer with the given number of bits.
    """
    return (-2**(bits - 1), 2**(bits - 1) - 1)


# Causes random.uniform(min,max) to return 'inf'.
# def float_bounds(bits: int) -> tuple[float, float]:
#     """
#     Returns (min, max) bounds for IEEE 754 floating-point types based on bit width.
#     Supports 32 (float) and 64 (double) bits.
#     """
#     if bits == 32:
#         # IEEE 754 single precision float
#         return (-3.4028235e+38, 3.4028235e+38)
#     elif bits == 64:
#         # IEEE 754 double precision float
#         return (-1.7976931348623157e+308, 1.7976931348623157e+308)
#     else:
#         raise ValueError(f"Unsupported float bit width: {bits}")


def float_bounds(bits: int) -> tuple[float, float]:
    """
    Returns usable float bounds for simulation/testing purposes.
    Avoids extreme IEEE754 values that cause overflow in computations.
    """
    if bits == 32:
        return (-1e38, 1e38)
    elif bits == 64:
        return (-1e300, 1e300)  # Still huge, but avoids overflow
    else:
        raise ValueError("Unsupported float bit width")



# pp = pprint.PrettyPrinter(indent=4,sort_dicts=False).pprint

