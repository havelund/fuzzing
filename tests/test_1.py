
from tests.test_utils import *


def test_count_future():
    spec = """
    rule p: count (5,5) MOVE(distance=42)
    """
    run(spec)


def test_count_future_exact():
    spec = """
    rule p: count 5 MOVE(distance=42)
    """
    run(spec)


def test_count_past():
    spec = """
    rule p: next next next next next countpast (3,3) MOVE(distance=42)
    """
    run(spec)


def test_count_past_exact():
    spec = """
    rule p: next next next next next countpast 3 MOVE(distance=42)
    """
    run(spec)


def test_freeze_future_past():
    run("""
    rule p1: next next next next next TURN(angle = 42)

    rule p2: count (3,3) MOVE()
    
    rule p3: always (
        TURN(angle=a?, number=n?, message=m?) => (
            (!CANCEL() until LOG(number=n,message=m))
            and
            (once ALIGN(angle=a))
        )
    )
    """)


def test_cmd_arg_interval_with_pattern():
    run("""
    rule p1: count (5,5) MOVE()

    rule p2: always MOVE(distance=a?) => 5 < a < 8
    """)


def test_next_pattern():
    run("""
    rule p: next next MOVE(number=x?) &> (next LOG(number = x))
    """)


def test_weak_until():
    run("""
    rule p:  CANCEL() WU MOVE()
    """)


def test_since():
    run("""
    rule p1: next next next next next MOVE(distance=1)

    rule p2: [](MOVE(distance=1) => ! CANCEL() S TURN(angle=180))
    """)


def test_time1():
    run("""
    rule p1: count (5,5) MOVE()

    rule p2: count (5,5) TURN()
    
    rule p3: always 
              MOVE(time=t1?) => 
                wnext 
                  always MOVE(time=t2?) => t1 < t2

    rule p4: always 
              TURN(time=t1?) => 
                wnext 
                  always TURN(time=t2?) => t1 < t2
    """)


def test_time2():
    run("""
    rule p: always any(time=t1?) => wnext any(time=t2?) => t1 < t2
    """, 2)


def test_empty_spec():
    run('')


def test_false_true():
    run('rule p: false -> true')


def test_now():
    run("""
    rule p: MOVE(time=10)
    """)


