
from __future__ import annotations

import random
import json

from temporal_logic import *
from utils import *


class Constants:
    MIN_INTEGER = 0
    MAX_INTEGER = 1_000_000


def testsuite_generation(config_file: str, cmd_enum_file: str, testsuite_file: str):
    # Read configuration file:
    try:
        with open(config_file, 'r') as file:
              config = json.load(file)
    except:
        error(f'ill-formed configuration file {config_file}')
    # Extract test suite and test size:
    testsuite_size: int = lookup_dict(config, "testsuite_size")
    test_size: int = lookup_dict(config, "test_size")
    # Extract constraints:
    constraints: list[Constraint] = extract_constraints(lookup_dict(config, "constraints"))
    # Read the command and enum json file:
    with open(cmd_enum_file, 'r') as file:
        cmd_enum_dictionaries = json.load(file)
    cmd_dict = lookup_dict(cmd_enum_dictionaries, 'cmd_dict')
    enum_dict = lookup_dict(cmd_enum_dictionaries, 'enum_dict')
    # Generate test suite and write it to a file:
    tests = generate_testsuite(cmd_dict, enum_dict, constraints, testsuite_size, test_size)
    with open(testsuite_file, "w") as file:
        json.dump(tests, file, indent=4)


def extract_constraints(constraint_objects: list[dict]) -> list[Constraint]:
    constraints: list[Constraint] = []
    for constraint_obj in constraint_objects:
        if lookup_dict(constraint_obj, "kind") == "int_parameter":
            command = lookup_dict(constraint_obj, "command")
            parameter = lookup_dict(constraint_obj, "parameter")
            min = lookup_dict(constraint_obj, "min")
            max = lookup_dict(constraint_obj, "max")
            constraint = Range(command, parameter, min, max)
            constraints.append(constraint)
        else:
            error(f'unknown constraint: {constraint_obj}')
    return constraints


def generate_testsuite(cmdDict: dict, enumDict: dict, constraints: list[Constraint], nr_tests: int, nr_cmds: int) -> TestSuite:
    test_suite: TestSuite = []
    count: int = 0
    failed: int = 0
    constrain_dicts(cmdDict, enumDict, constraints)
    while count != nr_tests:
        test = generate_test(cmdDict, enumDict, nr_cmds)
        if test_constraints(test, constraints) and test not in test_suite:
            count += 1
            test_suite.append([cmd.toDict() for cmd in test])
        else:
            failed += 1
    print(f'Tests violating constraints: {failed} out of {count + failed} = {failed * 100 / (count + failed):.2f}%')
    return test_suite


def constrain_dicts(cmdDict: dict, enumDict: dict, constraints: list[Constraint]):
    for constraint in constraints:
        match constraint:
            case Range(cmd_name, arg_name, min, max):
                update_range_of_int_parameter(cmdDict, cmd_name, arg_name, min, max)


def update_range_of_int_parameter(cmdDict: dict, cmd_name: str, arg_name: int, min: int, max: int):
    command = lookup_dict(cmdDict, cmd_name)
    parameter_list = lookup_dict(command, 'args')
    for parameter in parameter_list:
        if lookup_dict(parameter, "name") == arg_name:
            parameter["range_min"] = min
            parameter["range_max"] = max


def generate_test(cmdDict: dict, enumDict: dict, nr_cmds: int) -> Test:
    command_names = list(cmdDict.keys())
    test: Test = []
    for nr in range(nr_cmds):
        generated_command: Command = DotMap()
        command_name = random.choice(command_names)
        generated_command['name'] = command_name
        dict_command = lookup_dict(cmdDict, command_name)
        arguments = lookup_dict(dict_command, 'args')
        for arg in arguments:
            arg_name = lookup_dict(arg, 'name')
            arg_type = lookup_dict(arg, 'type')
            if arg_type == 'unsigned_arg':
                min = lookup_dict(arg, 'range_min')
                max = lookup_dict(arg, 'range_max')
                if min is None:
                    min = Constants.MIN_INTEGER
                if max is None:
                    max = Constants.MAX_INTEGER
                value = random.randrange(min, max)
            else:
                value = random.choice(lookup_dict(enumDict, arg_type))
            generated_command[arg_name] = value
        test.append(generated_command)
    return test
