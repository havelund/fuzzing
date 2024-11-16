
import random
import json

from src.fuzz.temporal_logic import *
from src.fuzz.utils import *


def testsuite_generation(config_file: str, cmd_enum_file: str, testsuite_file: str):
    """ Reads configuration file and cmd/enum dictionary file and generates a test suite.

    :param config_file: input configuration json file.
    :param cmd_enum_file: input command and enum dictionary json file
    :param testsuite_file: output testsuite json file.
    """
    # Read configuration file:
    try:
        with open(config_file, 'r') as file:
              config = json.load(file)
    except:
        error(f'ill-formed configuration file {config_file}')
    # Extract test suite and test size:
    testsuite_size: int = lookup_dict(config, INDEX.TESTSUITE_SIZE)
    test_size: int = lookup_dict(config, INDEX.TEST_SIZE)
    # Extract constraints:
    constraints: List[Constraint] = extract_constraints(lookup_dict(config, INDEX.CONSTRAINTS))
    # Read the command and enum json file:
    with open(cmd_enum_file, 'r') as file:
        cmd_enum_dictionaries = json.load(file)
    cmd_dict = lookup_dict(cmd_enum_dictionaries, INDEX.CMD_DICT)
    enum_dict = lookup_dict(cmd_enum_dictionaries, INDEX.ENUM_DICT)
    # Generate test suite and write it to a file:
    tests = generate_testsuite(cmd_dict, enum_dict, constraints, testsuite_size, test_size)
    with open(testsuite_file, "w") as file:
        json.dump(tests, file, indent=4)


def extract_constraints(constraint_objects: List[dict]) -> List[Constraint]:
    """Reads user defined constraints from a list of json constraint objects and returns
    the list of corresponding constraints".

    :param constraint_objects: the list of constraint json objects.
    :return: the list of constraints matching the constraint objects.
    """
    constraints: List[Constraint] = []
    for constraint_obj in constraint_objects:
        kind = lookup_dict(constraint_obj, INDEX.KIND)
        active = constraint_obj.get(INDEX.ACTIVE, True)
        if active:
            if kind == VALUE.RANGE:
                command = lookup_dict(constraint_obj, INDEX.CMD)
                argument = lookup_dict(constraint_obj, INDEX.ARG)
                min = lookup_dict(constraint_obj, INDEX.RANGE_MIN)
                max = lookup_dict(constraint_obj, INDEX.RANGE_MAX)
                constraint = Range(command, argument, min, max)
                constraints.append(constraint)
            elif kind == VALUE.INCLUDE:
                commands = lookup_dict(constraint_obj, INDEX.CMDS)
                constraint = Include(commands)
                constraints.append(constraint)
            elif kind == VALUE.EXCLUDE:
                commands = lookup_dict(constraint_obj, INDEX.COMMANDS)
                constraint = Exclude(commands)
                constraints.append(constraint)
            elif kind == VALUE.FOLLOWED_BY:
                cmd1 = lookup_dict(constraint_obj, INDEX.CMD1)
                cmd2 = lookup_dict(constraint_obj, INDEX.CMD2)
                constraint = Always(Implies(N(cmd1), Eventually(N(cmd2))))
                constraints.append(constraint)
            elif kind == VALUE.PRECEDES:
                cmd1 = lookup_dict(constraint_obj, INDEX.CMD1)
                cmd2 = lookup_dict(constraint_obj, INDEX.CMD2)
                constraint = Always(Implies(N(cmd2), Once(N(cmd1))))
                constraints.append(constraint)
            elif kind == VALUE.FOLLOWED_BY_NEXT:
                cmd1 = lookup_dict(constraint_obj, INDEX.CMD1)
                cmd2 = lookup_dict(constraint_obj, INDEX.CMD2)
                constraint = Always(Implies(N(cmd1), Next(N(cmd2))))
                constraints.append(constraint)
            elif kind == VALUE.PRECEDES_PREV:
                cmd1 = lookup_dict(constraint_obj, INDEX.CMD1)
                cmd2 = lookup_dict(constraint_obj, INDEX.CMD2)
                constraint = Always(Implies(N(cmd2), Previous(N(cmd1))))
                constraints.append(constraint)
            elif kind == VALUE.EVENTUALLY:
                command = lookup_dict(constraint_obj, INDEX.CMD)
                constraint = Eventually(N(command))
                constraints.append(constraint)
            else:
                error(f'unknown constraint: {constraint_obj}')
    return constraints


def generate_testsuite(cmd_dict: dict, enum_dict: dict, constraints: List[Constraint], nr_tests: int, nr_cmds: int) -> TestSuite:
    """Generates a test suite given and command dictionary, an enum dictionary, a list of constraints,
    and how many tests to generate and how many commands in a test to generate.

    :param cmd_dict: the command dictionary.
    :param enum_dict: the enum dictionary.
    :param constraints: the constraints.
    :param nr_tests: number of tests in the test suite.
    :param nr_cmds: number of commands in a test.
    :return: the generated test suite.
    """
    test_suite: TestSuite = []
    count: int = 0
    failed: int = 0
    constrain_dicts(cmd_dict, enum_dict, constraints)
    while count != nr_tests:
        test = generate_test(cmd_dict, enum_dict, nr_cmds)
        if test_constraints(test, constraints) and test not in test_suite:
            count += 1
            test_suite.append([cmd.toDict() for cmd in test])  # convert from dotMaps
        else:
            failed += 1
    print(f'Generated {count} tests - rejected {failed} tests ({failed * 100 / (count + failed):.2f}%)')
    return test_suite


def constrain_dicts(cmd_dict: dict, enum_dict: dict, constraints: List[Constraint]):
    """Constrains a command dictionary and enum dictionary according to a list of constraints.

    :param cmd_dict: the command dictionary.
    :param enum_dict: the enum dictionary.
    :param constraints: the constraints.

    The function has side effects, by updating the `cmd_dict` and the `enum_dict`.
    """
    for constraint in constraints:
        if isinstance(constraint, Range):
            cmd_name = constraint.cmd_name
            arg_name = constraint.arg_name
            min = constraint.min
            max = constraint.max
            update_range_of_int_argument(cmd_dict, cmd_name, arg_name, min, max)
        elif isinstance(constraint, Include):
            commands = constraint.cmd_names
            commands_to_delete = [cmd for cmd in cmd_dict.keys() if cmd not in commands]
            for cmd in commands_to_delete:
                del cmd_dict[cmd]
        elif isinstance(constraint, Exclude):
            for cmd in constraint.cmd_names:
                del cmd_dict[cmd]


def update_range_of_int_argument(cmd_dict: dict, cmd_name: str, arg_name: int, min: int, max: int):
    """Constrains the lower and upper bound of a command argument in the command dictionary.

    :param cmd_dict: the command dictionary.
    :param cmd_name: the command name.
    :param arg_name: the argument name.
    :param min: the minimal value it can take.
    :param max: the maximal value it can take.

    The function has side effects, by updating the `cmd_dict`.
    """
    command = lookup_dict(cmd_dict, cmd_name)
    argument_list = lookup_dict(command, INDEX.ARGS)
    for argument in argument_list:
        if lookup_dict(argument, INDEX.NAME) == arg_name:
            argument[INDEX.RANGE_MIN] = min
            argument[INDEX.RANGE_MAX] = max


def generate_test(cmd_dict: dict, enum_dict: dict, nr_cmds: int) -> Test:
    """Generates a single random test.

    :param cmd_dict: the command dictionary used for random selection of commands.
    :param enum_dict: the enum dictionary used for random selection of enum values.
    :param nr_cmds: the number of commands in a test.
    :return: the generated test.
    """
    command_names = list(cmd_dict.keys())
    test: Test = []
    for nr in range(nr_cmds):
        generated_command: Command = DotMap()
        command_name = random.choice(command_names)
        generated_command[INDEX.NAME] = command_name
        dict_command = lookup_dict(cmd_dict, command_name)
        arguments = lookup_dict(dict_command, INDEX.ARGS)
        for arg in arguments:
            arg_name = lookup_dict(arg, INDEX.NAME)
            arg_type = lookup_dict(arg, INDEX.TYPE)
            arg_length = lookup_dict(arg, INDEX.LENGTH)
            if arg_type == VALUE.UNSIGNED_ARG:
                default_min, default_max = limits_unsigned_int(arg_length)
                min = lookup_dict(arg, INDEX.RANGE_MIN)
                max = lookup_dict(arg, INDEX.RANGE_MAX)
                if min is None:
                    min = default_min
                if max is None:
                    max = default_max
                value = random.randrange(min, max)
            elif arg_type == VALUE.INTEGER_ARG:
                default_min, default_max = limits_signed_int(arg_length)
                min = lookup_dict(arg, INDEX.RANGE_MIN)
                max = lookup_dict(arg, INDEX.RANGE_MAX)
                if min is None:
                    min = default_min
                if max is None:
                    max = default_max
                value = random.randrange(min, max)
            elif arg_type == VALUE.FLOAT_ARG:
                default_min, default_max = limits_floating_point(arg_length)
                min = lookup_dict(arg, INDEX.RANGE_MIN)
                max = lookup_dict(arg, INDEX.RANGE_MAX)
                if min is None:
                    min = default_min
                if max is None:
                    max = default_max
                value = random.uniform(min, max)
            elif arg_type == VALUE.VAR_STRING_ARG:
                number_of_chars = int(arg_length / 8)
                value = '?' * number_of_chars
            else:
                value = random.choice(lookup_dict(enum_dict, arg_type))
            generated_command[arg_name] = value
        test.append(generated_command)
    return test


def generate_random_argument(arg: dict) -> Union[int, float, str]:
    ...
