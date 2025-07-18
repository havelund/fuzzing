
from fuzz import generate_tests, print_tests
from fuzz import Options, RefinementStrategy

spec = """
    rule time_moves_forward:
      always any(time=t1?) => wnext any(time=t2?) => t1 < t2

    rule two_turns: count 2 TURN()

    rule limit_degree:
      always TURN(angle=a?) => -90 <= a <= 90

    rule align_followed_by_turn: 
      always ALIGN(angle=a?) => eventually TURN(angle=a)

    rule turn_align_log: always (
        TURN(angle=a?, message=m?) => (
            (!CANCEL() until LOG(message=m))
            and
            (once ALIGN(angle=a))
        )
    )                  
    """


if __name__ == '__main__':
    Options.REFINEMENT_STRATEGY = RefinementStrategy.EVAL
    tests = generate_tests(spec, test_suite_size=1, test_size=10)
    print_tests(tests)
    for test in tests:
        print('=========')
        print('reset sut')
        print('=========')
        for cmd in test:
            print(f'send {cmd}')
