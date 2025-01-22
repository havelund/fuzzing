from typing import Optional, List

from src.fuzz.options import *
from src.fuzz.ltl_grammar import *
from src.fuzz.utils import debug, error, convert_z3_value, lookup_dict


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
    headline("SOLUTION FOUND")
    for i, cmd in enumerate(test):
        print(f"{i}: {cmd}")


def print_tests(tests: List[List[dict]]):
    """Pretty prints a list of generated tests.

    Tests can also be printed with just calling `print`. However, this will
    result in all tests being printed on one line, which is difficult to read.

    :param tests: the tests to be printed.
    """
    print()
    print('================')
    print('Generated tests:')
    print('================')
    print()
    print(json.dumps(tests, indent=4))


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


def refine_solver_using_to_smt(ast: LTLSpec, solver: Solver, end_time: int) -> ModelRef:
    print('Refining solution')
    for i in range(end_time):
        solver.push()
        command = command_dictionary.generate_random_smt_command()
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
    test = extract_and_verify_test(ast, refined_model, end_time)
    print_test(test)
    return test


def refine_solver_using_evaluate(ast: LTLSpec, solver: Solver, end_time: int) -> Test:
    print('Refining solution')
    test = extract_and_verify_test(ast, solver.model(), end_time).copy()
    for i in range(end_time):
        old_command = test[i]
        command = command_dictionary.generate_random_dict_command()
        test[i] = command
        if ast.evaluate(test):
            print(f'-- refinement step {i}: changed=True')
        else:
            print(f'refinement step {i}: changed=False')
            test[i] = old_command
    if not ast.evaluate(test):
        raise AssertionError('Model not satisfiable as expected')
    print_test(test)
    return test


def generate_tests(spec: Optional[str] = None, test_suite_size: Optional[int] = None, test_size: Optional[int] = None) -> list[Test]:
    if spec is None:
        spec_path = command_dictionary.spec_path
        if spec_path is None:
            raise ValueError(f"No specification is provided.")
        try:
            with open(spec_path, "r") as file:
                spec = file.read()
        except:
            raise ValueError(f"Specification file {spec_path} cannot be read or does not exist.")
    if test_suite_size is None:
        test_suite_size: int = command_dictionary.test_suite_size
        if test_suite_size is None:
            raise ValueError(f"No test suite size is provided.")
    if test_size is None:
        test_size: int = command_dictionary.test_size
        if test_size is None:
            raise ValueError(f"No test size is provided.")
    smt_rng_formula: BoolRef = command_dictionary.generate_smt_constraint(test_size)
    ast: LTLSpec = parse_spec(spec)
    smt_ltl_formula: BoolRef = ast.to_smt(test_size)
    smt_formula: BoolRef = And(smt_rng_formula, smt_ltl_formula)
    tests: list[Test] = []
    for test_nr in range(test_suite_size):
        print(f"Generating test number {test_nr}")
        test = generate_test(ast, smt_formula, test_size)
        tests.append(test)
    return tests


def generate_test(ast: LTLSpec, smt_formula: BoolRef, end_time: int) -> Test:
    solver = Solver()
    if solve_formula(solver, smt_formula, end_time) is not None:
        extract_and_verify_test(ast, solver.model(), end_time)
        if Options.REFINEMENT_STRATEGY == RefinementStrategy.PYTHON:
            test = refine_solver_using_evaluate(ast, solver, end_time)
        else:
            test = refine_solver_using_to_smt(ast, solver, end_time)
        return test
    else:
        print("The specification must contain inconsistent constraints!")
        sys.exit(1)


def extract_and_verify_test(ast: LTLSpec, model: ModelRef, end_time: int) -> Test:
    test = [extract_command(model.eval(timeline(i)), model) for i in range(end_time)]
    print('checking generated test against semantics')
    if not ast.evaluate(test):
        error(f"*** generated test does not satisfy LTL semantics:\n {test}")
    return test
