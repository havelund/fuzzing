
from operators import *


formula_seed = LTLNext(
    LTLNext(
        LTLNext(
            LTLNext(
                LTLNext(
                        LTLPredicate("mk_turn_cmd", [LTLConstraint("turn_angle", 42)]))))))


formula_real = LTLAlways(
        LTLImplies(
            LTLPredicate("mk_turn_cmd", []),
            LTLFreeze(
                'a',
                'turn_angle',
                LTLAnd(
                    LTLEventually(
                        LTLPredicate("mk_move_cmd", [LTLConstraint("move_speed", "a")])
                    ),
                    LTLOnce(
                        LTLPredicate("mk_move_cmd", [LTLConstraint("move_speed", "a")])
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
