
import json

import dict_clipper1


def read_dictionary() -> dict:
    dictionary = {
        "enumDict": dict_clipper1.enumDict,
        "cmdDict": dict_clipper1.cmdDict
    }
    return dictionary


def write_dictionary(dictionary: dict):
    with open("output.json", "w") as json_file:
        json.dump(dictionary, json_file, indent=4)


if __name__ == '__main__':
    dictionary = read_dictionary()
    write_dictionary(dictionary)
