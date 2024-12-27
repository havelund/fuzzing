from src.fuzz.solver import *


def run(spec):
    for _ in range(1):
        test = generate_test_satisfying_formula(spec, end_time=15)
        print_test(test)


def test_count_future():
    spec = """
    rule p: count (5,5) mk_move_cmd(distance=42)
    """
    run(spec)


def test_count_future_norule():
    spec = """
    norule p: count (5,5) mk_move_cmd(distance=42)
    """
    run(spec)


def test_count_past():
    spec = """
    rule p: next next next next next countpast (3,3) mk_move_cmd(distance=42)
    """
    run(spec)


def test_freeze_future_past():
    run("""
    rule p1: next next next next next mk_turn_cmd(turn_angle = 42)

    rule p2: count (3,3) mk_move_cmd()
    
    rule p3: always (
        mk_turn_cmd(turn_angle=a?) => (
            (!mk_cancel_cmd() until mk_log_cmd(data=a))
            and
            (once mk_align_cmd(turn_angle=a))
        )
    )
    """)


def test_cmd_arg_interval_with_pattern():
    run("""
    rule p1: count (5,5) mk_move_cmd()
    rule p2: always mk_move_cmd(distance=a?) => 2000 < a < 10000
    """)


def test_next_pattern():
    run("""
    rule p: next next mk_move_cmd(distance=x?) &> (next mk_log_cmd(data = x))
    """)


def test_weak_until():
    run("""
    rule p:  mk_cancel_cmd() WU mk_move_cmd()
    """)


def test_since():
    run("""
    rule p1: next next next next next mk_move_cmd(distance=0)

    rule p2: [](mk_move_cmd(distance=0) => ! mk_cancel_cmd() S mk_turn_cmd(turn_angle=180))
    """)


def test_time1():
    run("""
    rule p1: count (5,5) mk_move_cmd()

    rule p2: count (5,5) mk_turn_cmd()
    
    rule p3: always 
              mk_move_cmd(time=t1?) => 
                next 
                  always mk_move_cmd(time=t2?) => t1 < t2

    rule p4: always 
              mk_turn_cmd(time=t1?) => 
                next 
                  always mk_turn_cmd(time=t2?) => t1 < t2
    """)


def test_time2():
    run("""
    rule p: always any(time=t1?) => wnext any(time=t2?) => t1 < t2
    """)

def test_empty_spec():
    run('')




