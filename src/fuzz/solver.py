from typing import Optional

from src.fuzz.ltl_grammar import *
from src.fuzz.utils import debug, error, convert_z3_value


def print_model(model: ModelRef, end_time: int):
    headline("SOLUTION FOUND")
    for i in range(end_time):
        try:
            cmd = model.eval(timeline(i), model_completion=False)
            print(f'{i:3}: {cmd}')
        except Exception as e:
            print(f'{i:3}: Error evaluating timeline({i}): {e}')
    print("---------------")


def print_test(test: Test):
    for i, cmd in enumerate(test):
        print(f"{i}: {cmd}")


def extract_command(command: Command, model: ModelRef) -> dict:
    """
    Extracts information from a Z3 Command datatype instance dynamically using
    the number of constructors and their fields.

    :param command: The Z3 Command datatype instance to extract data from.
    :param model: The Z3 model used to evaluate the values.
    :return: A dictionary containing the constructor name and field values.
    :raises ValueError: If the command does not match any constructor.
    """
    for i in range(Command.num_constructors()):
        constructor = Command.constructor(i)
        constructor_name = constructor.name()
        is_constructor = getattr(Command, f'is_{constructor_name}')
        if model.eval(is_constructor(command)):
            data = {'name': constructor_name}
            for j in range(constructor.arity()):
                field_selector = Command.accessor(i, j)
                field_name = field_selector.name()
                field_value = model.eval(field_selector(command), model_completion=True)
                simple_field_name = field_name[len(constructor_name) + 1:]
                data[simple_field_name] = convert_z3_value(field_value)
            return data
    raise ValueError("Unknown command type")


def solve_formula(solver: Solver, formula: BoolRef, end_time: int) -> Optional[ModelRef]:
    solver.add(formula)
    if solver.check() == sat:
        model = solver.model()
        print_model(model, end_time)
        return model
    else:
        print("No solution found.")
        return None


def refine_solver(ast: LTLSpec, solver: Solver, end_time: int) -> ModelRef:
    print('Refining solution')
    for i in range(end_time):
        solver.push()

        command = command_dictionary.generate_random_command()
        solver.add(timeline(i) == command)

        if solver.check() == sat:
            print(f'-- refinement step {i}: changed=True')
            extract_and_verify_test(ast, solver.model(), end_time)
            solver.pop()  # Undo temporary changes
            solver.add(timeline(i) == command)  # Keep the satisfiable constraint
        else:
            print(f'refinement step {i}: changed=False')
            solver.pop()  # Remove unsatisfiable constraint

    if solver.check() != sat:
        raise AssertionError('Model not satisfiable as expected')

    refined_model = solver.model()
    print_model(refined_model, end_time)
    return refined_model


def generate_test_satisfying_formula(spec: str, end_time: int) -> Test:
    smt_rng_formula: BoolRef = command_dictionary.generate_smt_constraint(end_time)
    ast: LTLSpec = parse_spec(spec)
    smt_ltl_formula: BoolRef = ast.to_smt(end_time)
    smt_formula: BoolRef = And(smt_rng_formula, smt_ltl_formula)
    #smt_formula: BoolRef = smt_ltl_formula  # TODO: delete
    debug(f"FINAL constraint: {smt_formula.sexpr()}")
    solver = Solver()
    if solve_formula(solver, smt_formula, end_time) is not None:
        extract_and_verify_test(ast, solver.model(), end_time)
        model = refine_solver(ast, solver, end_time)
        test = extract_and_verify_test(ast, model, end_time)
        return test
    else:
        sys.exit(1)


def extract_and_verify_test(ast: LTLSpec, model: ModelRef, end_time: int) -> Test:
    test = [extract_command(model.eval(timeline(i)), model) for i in range(end_time)]
    print('checking generated test against semantics')
    if not ast.evaluate(test):
        error(f"*** generated test does not satisfy LTL semantics:\n {test}")
    return test
