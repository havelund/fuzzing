
import argparse
import json
import importlib


def write_json_file(py_module: str, json_file: str):
    data = importlib.import_module(py_module.replace('.py', ''))
    dictionary = {
        "enum_dict": data.enumDict,
        "cmd_dict": data.cmdDict
    }
    with open(json_file, "w") as json_file:
        json.dump(dictionary, json_file, indent=4)


def main(args = None):
    # Obtain names of input file and output file:
    parser = argparse.ArgumentParser(description="Dictionary json file generator")
    parser.add_argument("py_module", help="command and enum Python module")
    parser.add_argument("json_file", help="command and enum Json file")
    parsed_args = parser.parse_args(args)
    py_module = parsed_args.py_module
    json_file = parsed_args.json_file
    print('Reading from:')
    print(f'  {py_module}')
    print('Writing to:')
    print(f'  {json_file}')

    # Generate file
    write_json_file(py_module, json_file)


if __name__ == '__main__':
    args = [
        'data.input.dict_clipper1.py',
        '../data/output/cmd_enum.json',
    ]
    main(args)

