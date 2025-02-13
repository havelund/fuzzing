
from src.fuzz import generate_tests, print_tests

spec = """
    rule range:
      always
        CMD5(cmd5_arg1=x1?, cmd5_arg5=x5?) =>
          (
            (x1 = "enum11" or x1 = "enum12")
            and
            (45 <= x5 <= 50)
          )

    rule response:
      always CMD2(cmd2_arg1=x?, cmd2_arg2="enum21") =>
        next (
          not (CMD2(cmd2_arg1=x, cmd2_arg2="enum21")) 
            until 
          CMD2(cmd2_arg1=x, cmd2_arg2="enum22")        
        )
    
    rule past:
      always CMD2(cmd2_arg1=x?, cmd2_arg2="enum22") =>
        once CMD2(cmd2_arg1=x, cmd2_arg2="enum21")
    """

if __name__ == '__main__':
    tests = generate_tests(spec, test_suite_size=2, test_size=5)
    print_tests(tests)
    for test in tests:
        print('=========')
        print('reset fsw')
        print('=========')
        for cmd in test:
            print(f'send {cmd}')
