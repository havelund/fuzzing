
from src.fuzz import generate_tests, print_tests

spec = """
    rule k1: eventually FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1="fuzz_val_2")
    rule k2: count (2,2) FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x?) => x="fuzz_val_2"
    """

if __name__ == '__main__':
    tests = generate_tests(spec, test_suite_size=10, test_size=25)
    print_tests(tests)
    for test in tests:
        print('=========')
        print('reset fsw')
        print('=========')
        for cmd in test:
            print(f'send {cmd}')