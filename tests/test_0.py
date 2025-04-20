
from tests.test_utils import *

"""
These examples test wellformedness constraints applied after parsing succeeds.
"""

def test_rule_name_duplicates():
    spec = """
    rule p1: not MOVE()
    rule p2: eventually MOVE()
    rule p3: eventually TURN()
    rule p1: eventually ALIGN()
    rule p2: eventually STOP()
    """
    run(spec)


def test_count_down():
    spec = """
    rule p: count (5,4) MOVE(distance=42)
    """
    run(spec)


def test_count_negative():
    spec = """
    rule p: count -1 MOVE(distance=42)
    """
    run(spec)


def test_wrong_command_name():
    spec = """
    rule p: next next next next next countpast (3,3) MOVES(distance=42)
    """
    run(spec)


def test_wrong_field_name():
    spec = """
    rule p: next next next next next countpast 3 MOVE(distances=42)
    """
    run(spec)


def test_wrong_value_type():
    run("""
    rule p1: next next next next next TURN(angle = "42")
    """)

def test_double_var_definition():
    run("""
    rule p2: count (3,3) MOVE(time=x?,distance=x?)
    """)

def test_vars_not_defined():
    run("""
    rule p3: always (
        TURN(angle=a, number=n?, message=m?) => (
            (!CANCEL() until LOG(number=n2,message=m))
            and
            (once ALIGN(angle=a))
        )
    )
    """)

def test_wrong_type_in_relation():
    run("""
    rule p1: count (5,5) MOVE()

    rule p2: always MOVE(distance=a?) => 5 < a = "8"
    """)


def test_wrong_type():
    try:
        run("""
        rule p: next next MOVE(message=x?) &> (next LOG(number = x))
        """)
    except:
        pass


def test_enum1():
    run("""
    rule p: PIC(quality=image_quality.HIGH) => always PIC(quality=q?) => q = image_quality.high
    """)


def test_enum2():
    run("""
    rule p: PIC(quality=image_quality.high) => always PIC(quality=q?) => q = image_quality.HIGH
    """)


def test_enum3():
    run("""
    rule p: PIC(quality="high") => always PIC(quality=q?) => q = image_quality.high
    """)


def test_enum4():
    run("""
     rule p: PIC(quality=image_quality.high) => always PIC(quality=q?) => q = "HIGH"
     """)


def test_enum5():
    run("""
    rule p: PIC(quality=image_quality.high) => always PIC(quality=q?) => q = speed.slow
    """)


def test_undefined_variable():
    run("""
    rule p: PIC(quality=image_quality.high) => always PIC(quality=q?) => q_ups = image_quality.high
    """)


def test_float_constraints():
    run("""
    rule p1: eventually MOVE(number=2.4, speed=2.5)
    """)