from operators import *

formula_seed = LTLNext(
    LTLNext(
        LTLNext(
            LTLNext(
                LTLNext(
                    LTLPredicate("mk_move_cmd", [LTLConstraint("move_speed", 0)]))))))

# [](move(0) -> !cancel S turn(180))
formula_real = LTLAlways(
    LTLImplies(
        LTLPredicate("mk_move_cmd", [LTLConstraint("move_speed", 0)])
        ,
        LTLSince(
            LTLNot(
                LTLPredicate("mk_cancel_cmd", [])
            ),
            LTLPredicate("mk_turn_cmd", [LTLConstraint("turn_angle", 180)])
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


