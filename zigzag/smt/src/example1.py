
from operators import *


formula_seed = LTLPredicate(lambda env, t:
                         And(Command.is_mk_turn_cmd(timeline(5)), Command.turn_angle(timeline(5)) == 42))


formula_real_OLD = LTLAlways(
        LTLImplies(
            LTLPredicate(lambda env, t: Command.is_mk_turn_cmd(timeline(t))),
            LTLFreeze(
                lambda t: Command.turn_angle(timeline(t)),
                'a',
                LTLAnd(
                    LTLEventually(
                        LTLPredicate(lambda env, t:
                                             And([
                                                 Command.is_mk_move_cmd(timeline(t)),
                                                 Command.move_speed(timeline(t)) == env['a']
                                             ])
                                     )
                    ),
                    LTLOnce(
                        LTLPredicate(lambda env, t:
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


formula_real = LTLAlways(
        LTLImplies(
            LTLPredicate(lambda env, t: Command.is_mk_turn_cmd(timeline(t))),
            LTLFreeze(
                'a',
                'turn_angle',
                LTLAnd(
                    LTLEventually(
                        LTLPredicate(lambda env, t:
                                             And([
                                                 Command.is_mk_move_cmd(timeline(t)),
                                                 Command.move_speed(timeline(t)) == env['a']
                                             ])
                                     )
                    ),
                    LTLOnce(
                        LTLPredicate(lambda env, t:
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

formula = LTLAnd(formula_seed, formula_real)


if __name__ == '__main__':
    end_time = 20
    critical_steps = {5}
    test = generate_test_satisfying_formula(timeline, end_time, critical_steps, formula, generate_command, extract_command, solver)
    for i, cmd in enumerate(test):
        print(f"{i}: {cmd}")
