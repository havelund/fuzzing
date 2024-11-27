from operators import *
from commands import *
import random

# X X X X X move(0)
formula_seed = ExpressionConstraint(lambda env, t:
                                    And(Command.is_mk_move_cmd(timeline(5)), Command.move_speed(timeline(5)) == 0))
# [](move(0) -> !cancel S turn(180))
formula_real = Always(
    LogicImplies(
        ExpressionConstraint(lambda env, t:
                             And(Command.is_mk_move_cmd(timeline(t)), Command.move_speed(timeline(t)) == 0)
                             )
        ,
        Since(
            LogicNot(
                ExpressionConstraint(lambda env, t:
                                     Command.is_mk_cancel_cmd(timeline(t))
                                     )
            ),
            ExpressionConstraint(lambda env, t:
                                 And(Command.is_mk_turn_cmd(timeline(t)),
                                     Command.turn_angle(timeline(t)) == 180))
        )
    )
)

formula = LogicAnd(formula_seed, formula_real)


if __name__ == '__main__':
    end_time = 20
    critical_steps = {5}
    test = generate_test_satisfying_formula(timeline, end_time, critical_steps, formula, generate_command, extract_command, solver)
    for cmd in test:
        print(cmd)




