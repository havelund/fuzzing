
from fuzz import generate_tests, test_constraint, pp
from dictionaries.dict_clipper1 import cmdDict, enumDict

if __name__ == '__main__':
    tests = generate_tests(cmdDict, enumDict, test_constraint, 10, 5)
    pp(tests)

