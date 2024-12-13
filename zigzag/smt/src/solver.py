from typing import Optional

from zigzag.smt.src.ltl_grammar import *


def print_model(model: ModelRef, end_time: int):
    print("===============")
    print("Solution found!")
    print("===============")
    for i in range(end_time):
        cmd = model.eval(timeline(i))
        print(f'{i:3}: {cmd}')
    print("---------------")


def print_test(test: utils.Test):
    for i, cmd in enumerate(test):
        print(f"{i}: {cmd}")


def solve_formula(solver: Solver, formula: BoolRef, end_time: int) -> Optional[ModelRef]:
    solver.add(formula)
    if solver.check() == sat:
        model = solver.model()
        print_model(model, end_time)
        return model
    else:
        print("No solution found.")
        return None


def refine_solver(solver: Solver, end_time: int) -> ModelRef:
    for i in range(end_time):
        solver.push()

        command = generate_command()
        solver.add(timeline(i) == command)

        if solver.check() != sat:
            satisfied = False
        else:
            satisfied = True

        solver.pop()

        if satisfied:
            solver.add(timeline(i) == command)

    if solver.check() != sat:
        assert False, 'model not satisfiable as expected'
    refined_model = solver.model()
    print_model(refined_model, end_time)
    return refined_model


def generate_test_satisfying_formula(spec: str, end_time: int) -> utils.Test:
    ast: LTLSpec = parse_spec(spec)
    smt_formula: BoolRef = ast.evaluate(end_time)
    solver = Solver()
    if solve_formula(solver, smt_formula, end_time):
        model = refine_solver(solver, end_time)
        return [extract_command(model.eval(timeline(i)), model) for i in range(end_time)]
    else:
        sys.exit(1)

