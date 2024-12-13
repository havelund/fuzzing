from zigzag.smt.src.solver import *


spec = """
rule p1: next next next next next mk_move_cmd(move_speed=0)

rule p2: 
  [](
    mk_move_cmd(move_speed=0) -> 
      ! mk_cancel_cmd() S mk_turn_cmd(turn_angle=180)
    )
"""


if __name__ == '__main__':
    test = generate_test_satisfying_formula(spec, end_time=5)
    print_test(test)
