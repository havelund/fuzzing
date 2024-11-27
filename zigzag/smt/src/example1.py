
from operators import *
from commands import *


formula_seed = ExpressionConstraint(lambda env, t:
                         And(Command.is_mk_turn_cmd(timeline(5)), Command.turn_angle(timeline(5)) == 42))


formula_real = Always(
        LogicImplies(
            ExpressionConstraint(lambda env, t: Command.is_mk_turn_cmd(timeline(t))),
            FreezeAsIn(
                lambda t: Command.turn_angle(timeline(t)),
                'a',
                LogicAnd(
                    Eventually(
                        ExpressionConstraint(lambda env, t:
                                             And([
                                                 Command.is_mk_move_cmd(timeline(t)),
                                                 Command.move_speed(timeline(t)) == env['a']
                                             ])
                                             )
                    ),
                    Once(
                        ExpressionConstraint(lambda env, t:
                                             And([
                                                 Command.is_mk_move_cmd(timeline(t)),
                                                 Command.move_speed(timeline(t)) == env['a']
                                             ])
                                             )
                    )
                )
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
