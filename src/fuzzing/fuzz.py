
"""
Script Name: fuzz.py
Description: This script generates a test suite from a command and an enum dictionary.
A test suite is a list of tests, where a test is a list of commands.
It is driven by a configuration file where one provides the size of the test suite (number of tests),
the size of each test (number of commands in each test), and constraints.
Usage: python fuzz.py config.json cmd_enum_dict_file.json testsuite_file.json
"""

import argparse

from src.fuzzing.core import testsuite_generation


def main(args = None):
    """
     Main function to parse command-line arguments and process the data.

     Command-line arguments:
         --input (str): Path to the configuration json file.
         --input (str): Path to the command and enum dictionary json file.
         --output (str): Path to the generated test suite json file.
     """
    # Define input arguments to script:
    parser = argparse.ArgumentParser(description="Test suite generator")
    parser.add_argument("config_file", help="input configuration file as a json file")
    parser.add_argument("dictionary_file", help="input command and enum dictionaries as a json file")
    parser.add_argument("testsuite_file", help="output test suite as a json file")
    # Parse provided input arguments:
    parsed_args = parser.parse_args(args)
    config_file = parsed_args.config_file
    cmd_enum_file = parsed_args.dictionary_file
    testsuite_file = parsed_args.testsuite_file
    print('Reading configuration file from:')
    print(f'  {config_file}')
    print('Reading command and enum dictionaries from:')
    print(f'  {cmd_enum_file}')
    print('Writing test suite to:')
    print(f'  {testsuite_file}')
    # Generate test suite:
    testsuite_generation(config_file, cmd_enum_file, testsuite_file)


if __name__ == '__main__':
    # Testing script:
    data = '/Users/khavelun/Desktop/development/pycharmworkspace/fuzzing/data/'
    args = [
        data + 'input/constraints/config.json',
        data + 'output/cmd_enum.json',
        data + 'output/testsuite.json'
    ]
    # main(args)
    main()

