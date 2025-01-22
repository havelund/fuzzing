
from src.fuzz import generate_tests, print_tests

spec = """
    rule range:
      always
        FUZZ_CMD_MIXED_5(fuzz_cmd5_arg_1=x1?, fuzz_cmd5_arg_5=x5?) =>
          (
            (x1 = "fuzz_val_1" or x1 = "fuzz_val_2")
            and
            (45 <= x5 <= 50)
          )

    rule response:
      always FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x?, fuzz_cmd2_arg_2="ENABLE") =>
        next (
          not (FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x, fuzz_cmd2_arg_2="ENABLE")) 
            until 
          FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x, fuzz_cmd2_arg_2="DISABLE")        
        )
    
    rule past:
      always FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x?, fuzz_cmd2_arg_2="DISABLE") =>
        once FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1=x, fuzz_cmd2_arg_2="ENABLE")
    """

if __name__ == '__main__':
    tests = generate_tests(spec, test_suite_size=10, test_size=30)
    print_tests(tests)
    for test in tests:
        print('=========')
        print('reset fsw')
        print('=========')
        for cmd in test:
            print(f'send {cmd}')
