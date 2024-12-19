
from zigzag.smt.src.solver import *

spec = """
rule p1: next next next next next mk_turn_cmd(turn_angle = 42)

rule p2: always (
           mk_turn_cmd() -> 
             [a := turn_angle] (
               (!mk_cancel_cmd() until mk_move_cmd(move_speed=a))
               and
               (once mk_move_cmd(move_speed=a))
             )
          )

rule p3: always (
           mk_move_cmd() ->
             [a := move_speed]
               sofar (
                 mk_move_cmd() implies mk_move_cmd(move_speed=a)
               )
         )

"""

spec1 = """
rule p1: count (5,5) mk_move_cmd()
#rule p2: always (mk_move_cmd() -> [a := move_speed] (2000 < a < 10000))
#rule p:  (mk_cancel_cmd() WU mk_move_cmd())
rule p3: always (mk_move_cmd() -> [a := move_speed] 100 <= a <= 110)
#rule p3: always mk_move_cmd(move_speed=a?) => a > 10
#rule p3: always (mk_move_cmd() -> [a := move_speed] a > 1000)
"""

if __name__ == '__main__':
    test = generate_test_satisfying_formula(spec1, end_time=10)
    print_test(test)
