
from fuzz import generate_tests, TestSuite, Options

spec = """
    rule at_least_one_turn_and_send_and_two_moves:
      eventually TURN() and eventually SEND() and count 2 MOVE() 

    rule move_stop:
      always MOVE(number=n?) => eventually STOP(number=n)
    
    rule stop_move:
      always STOP(number=n?) => prev !STOP(number=n) since MOVE(number=n)
    
    rule limit_turn_degree:
      always TURN(angle=a?) => -10 <= a <= 10

    rule send_preceded_by_pic:
      always SEND(message=m?,images=i?) => 
        (
          m matches /\d\d\d\.img/ and
          once PIC(images=j?, message=m, quality="high") &> j >= i
        )
          
    rule time_increases:
      always any(time=t1?) => wnext any(time=t2?) =>  t1 + 10 < t2      
    """


if __name__ == '__main__':
    tests: TestSuite = generate_tests(spec=spec, test_suite_size=2, test_size=10)
    for test in tests:
        print(f'RESET_FSW')
        for cmd in test:
            print(cmd)