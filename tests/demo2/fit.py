
from src.fuzz import generate_tests, print_tests
from src.fuzz.options import Options, RefinementStrategy

spec = """
    rule time_progresses: 
      always any(time=t1?) => wnext any(time=t2?) => t1 < t2

    rule two_turns: count 2 TURN()
    
    rule limit_degree:
      always TURN(angle=a?) => -90 <= a <= 90
    
    rule turn_align_log: always (
        TURN(angle=a?, message=m?) => (
            (!CANCEL() until LOG(message=m))
            and
            (once ALIGN(angle=a))
        )
    )
    """


if __name__ == '__main__':
    Options.REFINEMENT_STRATEGY = RefinementStrategy.SMT
    tests = generate_tests(spec, test_suite_size=3, test_size=10)
    print_tests(tests)
    for test in tests:
        print('=========')
        print('reset fsw')
        print('=========')
        for cmd in test:
            print(f'send {cmd}')

