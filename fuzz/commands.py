"""
This module provides data structures and functions for initializing the variable:

    command_dictionary: FSWCommandDictionary

which will store the contents of the command and enumeration XML files defining the commands
and the enumeration types of the command arguments. This variable is visible throughout the
application code as a global variable.

It is necessary to make it a global variable initialized as the first thing in order to
make the Z3 SMT solver able to construct the corresponding type of commands.
"""

from dataclasses import dataclass
from enum import Enum
import json
import random
import string
from typing import Callable, Optional
import typing
from abc import ABC, abstractmethod
from pprint import pprint

from z3 import *

from fuzz.gencmds import generate_commands
from fuzz.utils import inspect, error, headline, unsigned_int_bounds, signed_int_bounds, float_bounds
from fuzz.options import Options


# ==================================================================
# The fundamental data types used by Z3, name the type of command
# and the timeline representing the list of generated commands.
# ==================================================================

Command: Datatype = None
timeline: Function = None


# ==================================================================
# Types of arguments as Python datatypes (in contrast to Z3 types).
# These types are used for type checking a specification.
# ==================================================================

class BaseType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"


@dataclass
class EnumType:
    name: str
    values: list[str]


FieldType = typing.Union[BaseType, EnumType]

VariableTypeEnvironment = dict[str, FieldType]
CommandTypeEnvironment = dict[str, VariableTypeEnvironment]


# ==================================================================
# Definition of types representing arguments to commands.
# ==================================================================

class FSWArgument(ABC):
    def __init__(self, name: str, length: int):
        self.name = name
        self.length = length

    @abstractmethod
    def random_python_value(self) -> object:
        """Generate a random Python value for the argument."""
        raise NotImplementedError()

    @abstractmethod
    def random_value(self) -> ExprRef:
        """Generate a random SMT value for the argument."""
        raise NotImplementedError()

    @abstractmethod
    def smt_type(self) -> Sort:
        """Return the SMT type for the argument."""
        raise NotImplementedError()

    @abstractmethod
    def field_type(self) -> FieldType:
        """Return the Python type for the argument."""
        raise NotImplementedError()

    @abstractmethod
    def smt_constraint(self, value: ExprRef) -> BoolRef:
        """Return the SMT constraint for the argument"""
        raise NotImplementedError()


class FSWUnassignedIntArgument(FSWArgument):
    """An integer argument."""

    def __init__(self, name: str, length: int, min: int, max: int):
        super().__init__(name, length)
        default_min, default_max = unsigned_int_bounds(length)
        self.min = min if min is not None else default_min
        self.max = max if max is not None else default_max

    def random_python_value(self) -> int:
        return random.randint(self.min, self.max)

    def random_value(self) -> IntNumRef:
        return IntVal(self.random_python_value())

    def smt_type(self) -> Sort:
        return IntSort()

    def field_type(self) -> FieldType:
        return BaseType.INT

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return And(self.min <= value, value <= self.max)


class FSWIntArgument(FSWArgument):
    """An integer argument."""

    def __init__(self, name: str, length: int, min: int, max: int):
        super().__init__(name, length)
        default_min, default_max = signed_int_bounds(length)
        self.min = min if min is not None else default_min
        self.max = max if max is not None else default_max

    def random_python_value(self) -> int:
        return random.randint(self.min, self.max)

    def random_value(self) -> IntNumRef:
        return IntVal(self.random_python_value())

    def smt_type(self) -> Sort:
        return IntSort()

    def field_type(self) -> FieldType:
        return BaseType.INT

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return And(self.min <= value, value <= self.max)


class FSWFloat32Argument(FSWArgument):
    """A 32 bit floating point argument."""

    def __init__(self, name: str, length: int, min: float, max: float):
        super().__init__(name, length)
        default_min, default_max = float_bounds(32)
        self.min = min if min is not None else default_min
        self.max = max if max is not None else default_max

    def random_python_value(self) -> float:
        return random.uniform(self.min, self.max)

    def random_value(self) -> FPNumRef:
        return RealVal(self.random_python_value())

    def smt_type(self) -> Sort:
        return RealSort()

    def field_type(self) -> FieldType:
        return BaseType.FLOAT

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return And(value >= self.min, value <= self.max)


class FSWFloat64Argument(FSWArgument):
    """A 64 bit floating point argument."""

    def __init__(self, name: str, length: int, min: float, max: float):
        super().__init__(name, length)
        default_min, default_max = float_bounds(64)
        self.min = min if min is not None else default_min
        self.max = max if max is not None else default_max

    def random_python_value(self) -> float:
        return random.uniform(self.min, self.max)

    def random_value(self) -> FPNumRef:
        return RealVal(self.random_python_value())

    def smt_type(self) -> Sort:
        return RealSort()

    def field_type(self) -> FieldType:
        return BaseType.FLOAT

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return And(value >= self.min, value <= self.max)


class FSWStringArgument(FSWArgument):
    """A string argument."""

    def __init__(self, name: str, length: int):
        super().__init__(name, length)
        self.ascii = [StringVal(chr(c)) for c in range(128)]

    def random_python_value(self) -> str:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(self.length))
        return random_string

    def random_value(self) -> ExprRef:
        return StringVal(self.random_python_value())

    def smt_type(self) -> Sort:
        return StringSort()

    def field_type(self) -> FieldType:
        return BaseType.STRING

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return Length(value) <= self.length


class FSWEnumArgument(FSWArgument):
    """An enumeration type argument."""

    def __init__(self, name: str, length: int, typ: str, enum_values: list[str]):
        super().__init__(name, length)
        self.typ = typ
        self.enum_values = enum_values

    def random_python_value(self) -> str:
        return random.choice(self.enum_values)

    def random_value(self) -> ExprRef:
        value = self.random_python_value()
        datatype = command_dictionary.get_enum_datatype(self.typ)
        return getattr(datatype, value)

    def smt_type(self) -> Sort:
        return command_dictionary.get_enum_datatype(self.typ)

    def field_type(self) -> FieldType:
        return EnumType(self.typ, self.enum_values)

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return BoolVal(True)


# ==================================================================
# Type of FSW commands.
# ==================================================================

class FSWCommand:
    """A flight software command."""

    def __init__(self, name: str, arguments: list[FSWArgument]):
        self.name = name
        self.arguments = arguments


# ==================================================================
# The command dictionary.
# ==================================================================

class FSWCommandDictionary:
    """The key dictionary of commands and their types.

    Attributes:
        enum_dict: the enumeration type dictionary generated from XML.
        cmd_dict: the command dictionary generated from XML.
        spec_file: path to file containing specification of constraints.
        test_suite_size: the number of tests to be generated.
        test_size: the number of commands in a single test.
        enum_types: mapping from names of enumerated types to the Z3 datatypes.  # TODO
        commands: the commands defined in the XML file, represented as class objects.
    """

    def __init__(self, enum_dict: dict, cmd_dict: dict, spec_file: Optional[str], test_suite_size: Optional[int], test_size: Optional[int]):
        self.enum_dict = enum_dict
        self.cmd_dict = cmd_dict
        self.spec_file = spec_file
        self.test_suite_size = test_suite_size
        self.test_size = test_size
        self._validate_dicts()
        self.enum_types: dict[str, Datatype] = {}
        self.commands: list[FSWCommand] = []
        self._initialize()

    def print_dictionaries(self):
        """Prints the enumeration and command dictionaries read in from XML files."""
        headline('ENUM DICT')
        pprint(self.enum_dict)
        headline('CMD DICT:')
        pprint(self.cmd_dict)

    def _validate_dicts(self):
        """Validates that the dictionaries are wellformed.
        This means that:
        - commands have an `args` field mapping to a list
        - each argument must have the following entries `name`, `length`, and `type`.
        """
        for cmd_name, cmd_data in self.cmd_dict.items():
            if 'args' not in cmd_data or not isinstance(cmd_data['args'], list):
                raise ValueError(f"Command {cmd_name} is missing 'args' or 'args' is not a list.")
            for arg in cmd_data['args']:
                if not all(key in arg for key in ['name', 'length', 'type']):
                    raise ValueError(f"Argument in command {cmd_name} is missing required keys.")

    def _initialize(self):
        """Initializes the state."""
        commands: list[FSWCommand] = []
        for cmd_name in self.cmd_dict:
            arguments: list[FSWArgument] = []
            for arg_in_dict in self.cmd_dict[cmd_name]['args']:
                name = arg_in_dict['name']
                length = arg_in_dict['length']
                typ = arg_in_dict['type']
                min = arg_in_dict.get('range_min', None)
                max = arg_in_dict.get('range_max', None)
                argument: FSWArgument = None
                if typ == 'unsigned_arg':
                    argument = FSWUnassignedIntArgument(name, length, min, max)
                elif typ == 'integer_arg':
                    argument = FSWIntArgument(name, length, min, max)
                elif typ == 'float_arg':
                    if length == 32:
                        argument = FSWFloat32Argument(name, length, min, max)
                    elif length == 64:
                        argument = FSWFloat64Argument(name, length, min, max)
                    else:
                        raise ValueError(f'Length {length} not valid for command {cmd_name} argument {name}')
                elif typ == 'var_string_arg':
                    argument = FSWStringArgument(name, length)
                elif typ in self.enum_dict:
                    enum_values = self.enum_dict[typ]
                    argument = FSWEnumArgument(name, length, typ, enum_values)
                else:
                    raise ValueError(f"Unknown type '{typ}' for argument {name} in command {cmd_name}")
                arguments.append(argument)
            commands.append(FSWCommand(cmd_name, arguments))
        self.commands = commands

    def add_enum_datatype(self, name: str, dt: Datatype):
        """Adds an enumeration datatype to the enum registry.

        :param name: name of the datatype.
        :param dt: the datatype.
        """
        self.enum_types[name] = dt

    def get_enum_datatype(self, name: str) -> Datatype:
        """Looks up an enumeration datatype.

        :param name: the name of the datatype.
        :return: the datatype with that name.
        """
        return self.enum_types[name]

    def to_smt_type(self) -> Datatype:
        """Creates and returns the `Command` Z3 type representing the type of commands."""
        try:
            # Declare enumerated types:
            for enum_name, enum_values in self.enum_dict.items():
                enum_type = Datatype(enum_name)
                for value in enum_values:
                    enum_type.declare(value)
                enum_type = enum_type.create()
                self.add_enum_datatype(enum_name, enum_type)
            # Declare commands:
            Command = Datatype('Command')
            for cmd in self.commands:
                fields = []
                for arg in cmd.arguments:
                    arg_name = f'{cmd.name}_{arg.name}'
                    smt_type = arg.smt_type()
                    fields.append((arg_name, smt_type))
                Command.declare(cmd.name, *fields)
            if Options.PRINT_CONSTRAINTS:
                headline('GENERATED COMMAND DATATYPE')
                print(Command)
            Command = Command.create()
            return Command
        except Exception as e:
            raise RuntimeError(f"Failed to create SMT datatype: {e}")

    def generate_smt_constraint(self, end_time: int) -> BoolRef:
        """
        Generate an SMT constraint for all commands' arguments
        across all time values from 0 to `end_time`.
        These include min/max constraints as well as string values
        which must be in some enumerated type.
        At each time point, if the command matches a specific type, its fields
        must satisfy the declared constraints.

        :param end_time: The maximum time value for the timeline.
        :return: A combined SMT constraint (BoolRef).
        """
        constraints = []
        for cmd in self.commands:
            is_cmd = getattr(Command, f'is_{cmd.name}')
            for t in range(end_time):
                cmd_constraints = []
                for arg in cmd.arguments:
                    arg_var = getattr(Command, f'{cmd.name}_{arg.name}')(timeline(t))
                    cmd_constraints.append(arg.smt_constraint(arg_var))
                command_constraint = Or(Not(is_cmd(timeline(t))), And(cmd_constraints))
                constraints.append(command_constraint)

        # Return combined constraints
        return And(constraints) if constraints else BoolVal(True)

    def generate_random_smt_command(self) -> Command:
        """Generates a random Z3 command. Used for test refinement with Z3."""
        command: FSWCommand = random.choice(self.commands)
        arguments = [arg.random_value() for arg in command.arguments]
        constructor = getattr(Command, command.name)
        return constructor(*arguments)

    def generate_random_dict_command(self) -> dict:
        """generates a random Python command. Used for test refinement with just Python."""
        fsw_command: FSWCommand = random.choice(self.commands)
        command_name = {'name': fsw_command.name}
        arguments = {arg.name: arg.random_python_value() for arg in fsw_command.arguments}
        command = {**command_name, **arguments}
        return command

    def find_fsw_command(self, cmd_name: str) -> FSWCommand:
        """Finds and returns the FSW command with the given name.

        :param cmd_name: the command name.
        :return: the FSW command represention of the contents of the XML file for that command.
        """
        for fsw_cmd in self.commands:
            if fsw_cmd.name == cmd_name:
                return fsw_cmd
        raise ValueError(f'command name {cmd_name} not found')

    def generate_random_arguments_for_command(self, cmd_name: str) -> dict:
        """ Returns random argument values for arguments of a command.

        :param cmd_name: the name of the command.
        :return: mapping from argument names to random values.
        """
        fsw_command: FSWCommand = self.find_fsw_command(cmd_name)
        return {arg.name: arg.random_python_value() for arg in fsw_command.arguments}

    def get_argument_type(self, cmd_name: str, arg_name: str) -> SortRef:
        """Returns the Z3 type corresponding to an argument to a command.

        :param cmd_name: the command name.
        :param arg_name: the argument name.
        :return: The Z3 type of the argument.
        """
        for cmd in self.commands:
            if cmd_name == cmd.name:
                for arg in cmd.arguments:
                    if arg_name == arg.name:
                        return arg.smt_type()
                error(f'Unknown argument {arg_name} for command {cmd_name}')
        error(f'Unknown command name {cmd_name}')

    # def get_argument_type_constructor(self, cmd_name: str, arg_name: str) -> Callable[[str, Context | None], ArithRef]:
    #     """Get Python type constructor corresponding to an argument.
    #
    #     :param cmd_name: the command name.
    #     :param arg_name: the argument name.
    #     :return: the Python type constructor corresponding to the argument
    #     """
    #     smt_type = self.get_argument_type(cmd_name, arg_name)
    #     if smt_type == IntSort():
    #         return Int
    #     elif smt_type == RealSort():
    #         return Real
    #     elif smt_type == StringSort():
    #         return String
    #     else:  # TODO: it is missing the enumerated type case. But the function is not called.
    #         raise ValueError(f"Unsupported SMT type for command {cmd_name} and argument {arg_name}")

    def generate_command_type_env(self) -> CommandTypeEnvironment:
        """Generate an environment mapping command names to maps, mapping argument names to types."""
        cmd_env: CommandTypeEnvironment = {}
        for cmd in self.commands:
            arg_env: VariableTypeEnvironment = {}
            for arg in cmd.arguments:
                arg_env[arg.name] = arg.field_type()
            cmd_env[cmd.name] = arg_env
        return cmd_env


def initialize():
    """ Initialize the `command_dictionary` variable.

    It assumes the existence of a configration file in json format.
    The path to the configuration file is either determined by an environment
    variable `FUZZ_CONFIG_PATH`, or the default `fuzz_config.json` in the
    current directory.
    """
    global command_dictionary, Command, timeline
    config_path = os.getenv("FUZZ_CONFIG_PATH", os.path.join(os.getcwd(), "fuzz_config.json"))
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    cmd_files = config.get("cmd_files")
    if not cmd_files:
        raise ValueError("'cmd_files' not defined in configuration file {config}\nlocated at {config_path}")
    spec_file = config.get("spec_file")
    test_suite_size = config.get("test_suite_size")
    test_size = config.get("test_size")
    enum_dict, cmd_dict = generate_commands(cmd_files)
    command_dictionary = FSWCommandDictionary(enum_dict, cmd_dict, spec_file, test_suite_size, test_size)
    command_dictionary.print_dictionaries()
    Command = command_dictionary.to_smt_type()
    timeline = Function('timeline', IntSort(), Command)


# ==================================================================
# Initializing the command dictionary.
# ==================================================================

command_dictionary: FSWCommandDictionary = None
initialize()

