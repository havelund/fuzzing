
"""
Module Name: fuzz.py
Description: This module generates a test suite from a command and an enum dictionary
represented as XML files stored in a directory. A test suite is a list of tests, where a test
is a list of commands. It is driven by a configuration file where one provides the size of
the test suite (number of tests), the size of each test (number of commands in each test), and constraints.
"""

from typing import cast, Optional

from src.fuzz.gencmds import generate_commands
from src.fuzz.core import *


def generate_tests(fsw_dir: str, fsw_areas: List[str], spec: str = None) -> List[List[dict]]:
    """Generates a test suite, which is a list of tests, each consisiting of a list of commands.

    It reads definitions of commands and their argument types, including enumerations,
    from XML files stored in a given directory. It only generates commands for certain FSW areas,
    provided as an argument as well. A specification defines how many tests should be generated,
    how many commands in each test, and constraints on what sequences of commands should be generated.

    :param fsw_dir: the directory containing command and enumeration descriptions in XML format.
    :param fsw_areas: the FSW areas commands should be generated for.
    :param spec: specification of constraints.
    :return: the generated test suite, a list of tests, each being a list of commands.
    """
    if spec is None:
        spec = ''
        print('No constraints')
    else:
        print('Constraints:')
        print(spec)
    # Extract enumeration and commands from XML
    enum_dict, cmd_dict = generate_commands(fsw_dir, fsw_areas)
    # Extract test suite size, test size, and constrainst from config:
    #testsuite_size: int = cast(int, lookup_dict(config, INDEX.TESTSUITE_SIZE))
    testsuite_size: int = 10  # TODO
    #test_size: int = cast(int, lookup_dict(config, INDEX.TEST_SIZE))
    test_size: int = 15  # TODO
    # Generate and return test suite
    tests = generate_testsuite(cmd_dict, enum_dict, spec, testsuite_size, test_size)
    return tests


def print_tests(tests: List[List[dict]]):
    """Pretty prints a generated test.

    A test can also be printed with just calling `print`. However, this will
    result in all tests being printed on one line, which is difficult to read.

    :param tests: the test to be printed.
    """
    print()
    print('================')
    print('Generated tests:')
    print('================')
    print()
    print(json.dumps(tests, indent=4))


if __name__ == '__main__':
    # Brief test:
    from pathlib import Path
    base_path = Path(__file__).parent.resolve()
    fsw_path = str(base_path / '../../tests/data/xml/xml1')
    config_file = str(base_path / '../../tests/data/constraints/config1.json')
    fsw_areas = ['uvs']
    tests = generate_tests(fsw_path, fsw_areas, config_file)
    print_tests(tests)


