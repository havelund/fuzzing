
from formula_grammar import *

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
"""

if __name__ == '__main__':
    end_time = 20
    ast: LTLSpec = parse_spec(spec)
    smt_formula: BoolRef = ast.evaluate(end_time)
    test = generate_test_satisfying_formula(smt_formula, end_time)
    for i, cmd in enumerate(test):
        print(f"{i}: {cmd}")
