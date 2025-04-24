
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


def test_time3():
    run("""
    rule p: always any(time=t1?) => wnext any(time=t2?) => t2 > t1 + 10
    """)


def test_empty_spec():
    run('')


def test_false_true():
    run('rule p: false -> true')


def test_now():
    run("""
    rule p: MOVE(time=10)
    """)


def test_float_expressions():
    run("""
    rule p1: eventually MOVE(speed=s?) &> s = 2.5
    rule p2: eventually TURN(angle=a?) &> a = -20.5
    """)

def test_float_constraints():
    run("""
    rule p1: eventually MOVE(speed=2.5)
    rule p2: eventually TURN(angle=-20.5)
    """)

def test_arithmetic():
    run("""
    rule p1: eventually MOVE(speed=a?) &> eventually MOVE(speed=b?) &> b = (a + 4) / 2
    rule p2: eventually TURN(angle=a?) &> eventually TURN(angle=b?) &> a = b / 2 = 2.5
    """)

def test_string_lt_comparison():
    norun("""
    rule p1: MOVE()
    rule p2: always MOVE(message=m1?) => 
               wnext eventually MOVE(message=m2?) &> m1 < m2
    """, 3)

def test_string_concatenation():
    norun("""
    rule p1: eventually MOVE(message=m1?) &> 
               (m1 != "" and
               next
                 eventually MOVE(message=m2?) &> 
                   (m2 != "" and
                   next
                     eventually MOVE(message=m3?) &>
                       m3 = m2))
    """)

def test_modal_logic_notation():
    run("""
    rule p1: always [MOVE(distance=a?)] 5 < a < 8
    rule p2: next next <MOVE(number=x?)> next LOG(number = x)
    """)

def test_regular_expression1():
    run("""
    rule p0 : <MOVE(message=m?)> m matches /ab.*/
    rule p1 : next <MOVE(message=m?)> m matches /abc+.{5}/   # "abcD{5}"
    rule p2 : next next <MOVE(message=m?)> m matches /(abc){2,3}/
    rule p3 : next next next <MOVE(message=m?)> m matches /([P-R]|[p-r]){4,5}/   # "(Q"
    rule p4 : next next next next <MOVE(message=m?)> m matches /[p-r]{4,5}/
    rule p5 : next next next next next <MOVE(message=m?)> m matches /[pqr]{4,5}/ 
    rule p6 : next next next next next next <MOVE(message=m?)> m matches /[A-Zp-r]{4,5}/
    rule p7 : next next next next next next next <MOVE(message=m?)> m matches /[A-Zpqr]{4,5}/
    rule p8 : next next next next next next next next <MOVE(message=m?)> m matches /\w{2}\s{2}\d{2}/
    rule p9 : next next next next next next next next next <MOVE(message=m?)> m matches /\d{5}\w\w?\w{2}/
    """)

def test_regular_expression2():
    run("""
    rule p0 : <SEND(message=m?)> m matches /.+path\/file[0-9]+(((data)|(img))).*/
    """)

# /.+path\/file[0-9]+(((data)|(img))).*/
# /.*\[[A-Za-z]\w*\/[0-9]{3}\.(data|img)(\.\d{4}\-\d{2}\-\d{2})?\].*/

def test_regular_expression3():
    run("""
    rule p: (<SEND(message=m?)> m matches /data\-\d{3}\.txt/)
            and
            (next <SEND(message=m?)> m matches /data\-\d{3}\.txt/)
            and 
            (next next <SEND(message=m?)> m matches /data\-\d{3}\.txt/)
    """)


def test_enum1():
    run("""
     rule p: eventually 
               <PIC(quality=image_quality.high)> 
                 next <PIC(quality=q?)> q = image_quality.low
     """)

def test_enum2():
    run("""
     rule p: always 
               <PIC(quality=image_quality.high)> 
                 true
     """)

def test_enum3():
    run("""
     rule p: always 
               <PIC(quality=q?)> 
                 q = image_quality.low
     """)

def test_numbers():
    run("""
    rule p: always SCAN()
    """)

def test_next_prev_times():
    run("""
    rule p1: count 1 PIC()
    rule p2: always PIC() => next 4 SEND()
    rule p3: always PIC() => prev 2 STOP()
    """)