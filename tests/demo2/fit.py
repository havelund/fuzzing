
from src.fuzz import generate_tests, TestSuite

spec = """
    rule stop:
      always MOVE(number=n?) => eventually STOP(number=n)

    rule two_align: count 2 ALIGN()
    
    rule two_three_turns: count (2,3) TURN()
    
    rule limit_degree:
      always TURN(angle=a?) => -10 <= a <= 10
        
    rule align_followed_by_turn: 
      always ALIGN(angle=a?) => next ! ALIGN(angle=a) until MOVE()

    rule time_moves_forward:
      always any(time=t1?) => wnext any(time=t2?) => t1 < t2
    """


if __name__ == '__main__':
    tests: TestSuite = generate_tests(spec=spec, test_suite_size=2, test_size=10)
    for test_nr, test in enumerate(tests):
        print(f'\n=== test nr. {test_nr} ===\n')
        for cmd in test:
            print(cmd)