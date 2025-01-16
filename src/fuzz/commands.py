import json
import random
import string
from typing import Callable
from abc import ABC, abstractmethod
from pprint import pprint

from z3 import *




from src.fuzz.gencmds import generate_commands
from src.fuzz.utils import debug, error, headline

# Command = Datatype('Command')
#
# Command.declare('mk_move_cmd', ('mk_move_cmd_time', IntSort()), ('mk_move_cmd_number', IntSort()), ('mk_move_cmd_distance', IntSort()))
# Command.declare('mk_align_cmd', ('mk_align_cmd_time', IntSort()), ('mk_align_cmd_number', IntSort()), ('mk_align_cmd_turn_angle', IntSort()))
# Command.declare('mk_turn_cmd', ('mk_turn_cmd_time', IntSort()), ('mk_turn_cmd_number', IntSort()), ('mk_turn_cmd_turn_angle', IntSort()))
# Command.declare('mk_cancel_cmd', ('mk_cancel_cmd_time', IntSort()), ('mk_cancel_cmd_number', IntSort()))
# Command.declare('mk_stop_cmd', ('mk_stop_cmd_time', IntSort()), ('mk_stop_cmd_number', IntSort()))
# Command.declare('mk_capture_cmd', ('mk_capture_cmd_time', IntSort()), ('mk_capture_cmd_number', IntSort()), ('mk_capture_cmd_images', IntSort()))
# Command.declare('mk_send_cmd', ('mk_send_cmd_time', IntSort()), ('mk_send_cmd_number', IntSort()), ('mk_send_cmd_images', IntSort()))
# Command.declare('mk_log_cmd', ('mk_log_cmd_time', IntSort()), ('mk_log_cmd_number', IntSort()), ('mk_log_cmd_data', IntSort()))
#
# Command = Command.create()
#
# timeline = Function('timeline', IntSort(), Command)


DEFAULT_MIN_UINT = 0
DEFAULT_MAX_UINT = 2**32 - 1

DEFAULT_MIN_FLOAT32 = -3.4028235e+38
DEFAULT_MAX_FLOAT32 = 3.4028235e+38

DEFAULT_MIN_FLOAT64 = -1.7976931348623157e+308
DEFAULT_MAX_FLOAT64 = 1.7976931348623157e+308

Command: Datatype = None
timeline: Function = None


class FSWArgument(ABC):
    def __init__(self, name: str, length: int):
        self.name = name
        self.length = length

    @abstractmethod
    def random_value(self) -> ExprRef:
        """Generate a random value for the argument."""
        raise NotImplementedError()

    @abstractmethod
    def smt_type(self) -> Sort:
        """Return the SMT type for the argument."""
        raise NotImplementedError()

    @abstractmethod
    def smt_constraint(self, value: ExprRef) -> BoolRef:
        raise NotImplementedError()


class FSWUnassignedIntArgument(FSWArgument):
    def __init__(self, name: str, length: int, min: int, max: int):
        super().__init__(name, length)
        self.min = min if min is not None else DEFAULT_MIN_UINT
        self.max = max if max is not None else DEFAULT_MAX_UINT

    def random_value(self) -> IntNumRef:
        return IntVal(random.randint(self.min, self.max))

    def smt_type(self) -> Sort:
        return IntSort()

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return And(self.min <= value, value <= self.max)


class FSWFloat32Argument(FSWArgument):
    def __init__(self, name: str, length: int, min: float, max: float):
        super().__init__(name, length)
        self.min = min if min is not None else DEFAULT_MIN_FLOAT32
        self.max = max if max is not None else DEFAULT_MAX_FLOAT32

    def random_value(self) -> FPNumRef:
        random_float = random.uniform(self.min, self.max)
        return RealVal(random_float)

    def smt_type(self) -> Sort:
        return RealSort()

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return And(value >= self.min, value <= self.max)


class FSWFloat64Argument(FSWArgument):
    def __init__(self, name: str, length: int, min: float, max: float):
        super().__init__(name, length)
        self.min = min if min is not None else DEFAULT_MIN_FLOAT64
        self.max = max if max is not None else DEFAULT_MAX_FLOAT64

    def random_value(self) -> FPNumRef:
        random_float = random.uniform(self.min, self.max)
        return RealVal(random_float)

    def smt_type(self) -> Sort:
        return RealSort()

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return And(value >= self.min, value <= self.max)


class FSWStringArgument(FSWArgument):
    def __init__(self, name: str, length: int):
        super().__init__(name, length)

    def random_value(self) -> ExprRef:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(self.length))
        return StringVal(random_string)

    def smt_type(self) -> Sort:
        return StringSort()

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return Length(value) <= self.length


class FSWEnumArgument(FSWArgument):
    def __init__(self, name: str, length: int, enum_values: list[str]):
        super().__init__(name, length)
        self.enum_values = enum_values

    def random_value(self) -> ExprRef:
        random_enum = random.choice(self.enum_values)
        return StringVal(random_enum)

    def smt_type(self) -> Sort:
        return StringSort()

    def smt_constraint(self, value: ExprRef) -> BoolRef:
        return Or([value == StringVal(enum) for enum in self.enum_values])


class FSWCommand:
    def __init__(self, name: str, arguments: list[FSWArgument]):
        self.name = name
        self.arguments = arguments


class FSWCommandDictionary:
    def __init__(self, enum_dict: dict, cmd_dict: dict):
        self.enum_dict = enum_dict
        self.cmd_dict = cmd_dict
        self._validate_dicts()
        self.commands: list[FSWCommand] = []
        self._initialize()

    def print_dictionaries(self):
        headline('ENUM DICT')
        pprint(self.enum_dict)
        headline('CMD DICT:')
        pprint(self.cmd_dict)

    def _validate_dicts(self):
        for cmd_name, cmd_data in self.cmd_dict.items():
            if 'args' not in cmd_data or not isinstance(cmd_data['args'], list):
                raise ValueError(f"Command {cmd_name} is missing 'args' or 'args' is not a list.")
            for arg in cmd_data['args']:
                if not all(key in arg for key in ['name', 'length', 'type']):
                    raise ValueError(f"Argument in command {cmd_name} is missing required keys.")

    def _initialize(self):
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
                    argument = FSWEnumArgument(name, length, enum_values)
                else:
                    raise ValueError(f"Unknown type '{typ}' for argument {name} in command {cmd_name}")
                arguments.append(argument)
            commands.append(FSWCommand(cmd_name, arguments))
        self.commands = commands

    def to_smt_type(self) -> Datatype:
        try:
            Command = Datatype('Command')
            for cmd in self.commands:
                fields = []
                for arg in cmd.arguments:
                    arg_name = f'{cmd.name}_{arg.name}'
                    smt_type = arg.smt_type()
                    fields.append((arg_name, smt_type))
                Command.declare(cmd.name, *fields)
            Command = Command.create()
            return Command
        except Exception as e:
            raise RuntimeError(f"Failed to create SMT datatype: {e}")

    def generate_smt_constraint(self, end_time: int) -> BoolRef:
        """
        Generate an SMT constraint for all commands' arguments
        across all time values from 0 to `end_time`. At each time point,
        if the command matches a specific type, its fields must satisfy
        the declared constraints.

        :param end_time: The maximum time value for the timeline.
        :return: A combined SMT constraint (BoolRef).
        """
        constraints = []
        for cmd in self.commands:
            # Check if the timeline at a time point corresponds to the current command
            is_cmd = getattr(Command, f'is_{cmd.name}')
            for t in range(end_time):
                cmd_constraints = []
                for arg in cmd.arguments:
                    arg_var = getattr(Command, f'{cmd.name}_{arg.name}')(timeline(t))
                    cmd_constraints.append(arg.smt_constraint(arg_var))
                # Only enforce the argument constraints if the command matches
                constraints.append(Implies(is_cmd(timeline(t)), And(cmd_constraints)))

        return And(constraints) if constraints else BoolVal(True)

    def generate_random_command(self) -> Command:
        command: FSWCommand = random.choice(self.commands)
        arguments = [arg.random_value() for arg in command.arguments]
        constructor = getattr(Command, command.name)
        return constructor(*arguments)

    def get_argument_type(self, cmd_name: str, arg_name: str) -> SortRef:
        for cmd in self.commands:
            if cmd_name == cmd.name:
                for arg in cmd.arguments:
                    if arg_name == arg.name:
                        return arg.smt_type()
                error(f'Unknown argument {arg_name} for command {cmd_name}')
        error(f'Unknown command name {cmd_name}')

    def get_argument_type_constructor(self, cmd_name: str, arg_name: str) -> Callable[[str, Context | None], ArithRef]:
        smt_type = self.get_argument_type(cmd_name, arg_name)
        if smt_type == IntSort():
            return Int
        elif smt_type == RealSort():
            return Real
        elif smt_type == StringSort():
            return String
        else:
            raise ValueError(f"Unsupported SMT type for command {cmd_name} and argument {arg_name}")


def initialize():
    """
    ...
    export CONFIG_PATH=/etc/myproject/config.json
    python your_script.py
    """
    global command_dictionary, Command, timeline
    config_path = os.getenv("FUZZ_CONFIG_PATH", os.path.join(os.getcwd(), "fuzz_config.json"))
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    fsw_path = config.get("fsw_path")
    if not fsw_path:
        raise ValueError("'fsw_path' not defined in configuration file {config}\nlocated at {config_path}")
    fsw_areas = config.get("fsw_areas")
    enum_dict, cmd_dict = generate_commands(fsw_path, fsw_areas)
    command_dictionary = FSWCommandDictionary(enum_dict, cmd_dict)
    command_dictionary.print_dictionaries()
    Command = command_dictionary.to_smt_type()
    timeline = Function('timeline', IntSort(), Command)


command_dictionary: FSWCommandDictionary = None

initialize()

