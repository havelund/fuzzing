
from fuzz import generate_tests, TestSuite, Options

spec = """
    rule plan:
    eventually (
      MOVE() and next (not MOVE() until (PIC() and eventually MOVE()))
    )
    """

if __name__ == '__main__':
    tests: TestSuite = generate_tests(spec=spec, test_suite_size=2, test_size=10)
    for test in tests:
        print(f'RESET SUT')
        for cmd in test:
            print(cmd)