
"""
Script Name: cmds_to_json.py
Description: This script converts a collection of Python modules in a given
directory, each defining a `enumDict` and a `cmdDict`, to a Json file.
Usage: python cmds_to_json.py input_dir output_file.json
"""

import argparse
import json
import importlib.util
import os


def import_all_from_directory(directory: str):
    """ Imports and returns all Python modules in a given directory.

    The Python modules are assumed to each contain a `enumDict` and a `cmdDict`,
    containing respectively the types of command arguments, and the commands
    themselves.

    :param directory: path to directory containing Python modules (`.py` files).
    :return: list of imported Python modules.
    """
    imported_modules = []
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            file_path = os.path.join(directory, filename)
            module_name = os.path.basename(file_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            imported_modules.append(module)
    return imported_modules


def write_json_file(py_dir: str, json_file: str):
    """Reads Python modules with enum and command dictionaries and writes a json file
    containing all these.

    :param py_dir: path to directory containing Python modules (`.py` files).
    :param json_file: Json file to which all enum and command specifications are written.
    """

    modules = import_all_from_directory(py_dir)
    enum_dict: dict = {}
    cmd_dict: dict = {}
    for module in modules:
        print(f"Module name: {module.__name__}")
        if hasattr(module, 'enumDict'):
            print(f"  updating enumDict")
            enum_dict.update(module.enumDict)
        if hasattr(module, 'cmdDict'):
            print(f"  updating cmdDict")
            cmd_dict.update(module.cmdDict)
    dictionary = {
        "enum_dict": enum_dict,
        "cmd_dict": cmd_dict
    }
    with open(json_file, "w") as json_file:
        json.dump(dictionary, json_file, indent=4)


def main(args = None):
    """
     Main function to parse command-line arguments and process the data.

     Command-line arguments:
         --input (str): Path to the input directory.
         --output (str): Path to the output json file.
     """
    # Define input arguments to script:
    parser = argparse.ArgumentParser(description="Dictionary json file generator")
    parser.add_argument("py_dir", help="path to directory containing Python modules with dictionaries")
    parser.add_argument("json_file", help="resulting command and enum Json file")
    # Parse provided input arguments:
    parsed_args = parser.parse_args(args)
    py_dir = parsed_args.py_dir
    json_file = parsed_args.json_file
    print('Reading from directry:')
    print(f'  {py_dir}')
    print('Writing to:')
    print(f'  {json_file}')
    # Translate Python modules in `py_dir` to Json, written to `json_file`:
    write_json_file(py_dir, json_file)


if __name__ == '__main__':
    # Testing script:
    datadir = '/Users/khavelun/Desktop/development/pycharmworkspace/fuzzing/data/'
    args = [
        datadir + 'input/clipper1',
        datadir + 'output/cmd_enum.json'
    ]
    # main(args)
    main()
