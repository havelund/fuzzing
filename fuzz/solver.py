"""
Z3 solver functions.
"""
import time
from typing import Optional, List

from fuzz.options import *
from fuzz.ltl_grammar import *
from fuzz.utils import inspect, debug, error, convert_z3_value


def print_model(model: ModelRef, end_time: int):
    """Prints the timeline evaluated in a model.

    :param model: the model to evaluate the timeline in.
    :param end_time: the end time of the timeline.
    """
    headline("SOLUTION FOUND")
    for i in range(end_time):
        try:
            cmd = model.eval(timeline(i), model_completion=False)
            print(f'{i:3}: {cmd}')
        except Exception as e:
            print(f'{i:3}: Error evaluating timeline({i}): {e}')
    print("---------------")


def print_test(test: Test):
    """Prints a test, command by command.

    :param test: the test to print.
    """
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
    """Adds a formula to a solver and checks whether it has a model, which is returned if so.

    :param solver: the solver to add the formula to.
    :param formula: the formula to add to the solver.
    :param end_time: the end time of the timeline.
    :return: A model if the formula results in a model, and `None` if not.
    """
    solver.add(formula)
    if solver.check() == sat:
        model = solver.model()
        if Options.DEBUG_LEVEL >= 1:
            print_model(model, end_time)
        return model
    else:
        print("No solution found.")
        return None


def refine_solver_using_to_smt(ast: LTLSpec, solver: Solver, end_time: int) -> Test:
    """Refines a solver using Z3 itself, and returns a resulting test.

    :param ast: the specifiation of constraints.
    :param solver: the solver.
    :param end_time: the end time of the timeline.
    :return: the test extracted from the final extracted model.
    """
    debug(3, 'Refining solution')
    for i in range(end_time):
        solver.push()
        command = command_dictionary.generate_random_smt_command()
        solver.add(timeline(i) == command)
        if solver.check() == sat:
            debug(3, f'-- refinement step {i}: changed=True')
            extract_and_verify_test(ast, solver.model(), end_time)
            solver.pop()  # Undo temporary changes
            solver.add(timeline(i) == command)  # Keep the satisfiable constraint
        else:
            debug(3, f'refinement step {i}: changed=False')
            solver.pop()  # Remove unsatisfiable constraint
    if solver.check() != sat:
        raise AssertionError('Model not satisfiable as expected')
    refined_model = solver.model()
    test = extract_and_verify_test(ast, refined_model, end_time)
    if Options.DEBUG_LEVEL >= 1:
        print_test(test)
    return test


def refine_solver_using_evaluate(ast: LTLSpec, solver: Solver, end_time: int) -> Test:
    """Refines a test, and returns a resulting test.

    The refinement is performed at the command level: each command in the test is attempted replaced
    by a random command (including random arguments). If the new random command makes the
    specification fail the old command is kept and we move on to the next command.

    :param ast: the specifiation of constraints.
    :param solver: the solver.
    :param end_time: the end time of the timeline.
    :return: the final test.
    """
    debug(3, 'Refining solution')
    test = extract_and_verify_test(ast, solver.model(), end_time).copy()
    for i in range(end_time):
        old_command = test[i]
        new_command = command_dictionary.generate_random_dict_command()
        test[i] = new_command
        if ast.evaluate(test):
            debug(3, f'-- refinement step {i}: replacing {old_command} with {new_command}')
        else:
            debug(3, f'refinement step {i}: keeping {old_command}')
            test[i] = old_command
    if not ast.evaluate(test):
        raise AssertionError('Model not satisfiable as expected')
    if Options.DEBUG_LEVEL >= 1:
        print_test(test)
    return test


def refine_solver_using_evaluate_per_arg(ast: LTLSpec, solver: Solver, end_time: int) -> Test:
    """Refines a test, and returns a resulting test.

    The refinement is performed at the argyment level: each command in the test is attempted replaced
    by a random command (including random arguments). If the new random command makes the
    specification fail, then it is attempted to randomize each argument, keeping the command name.

    :param ast: the specifiation of constraints.
    :param solver: the solver.
    :param end_time: the end time of the timeline.
    :return: the final test.
    """
    debug(3, 'Refining solution')
    test = extract_and_verify_test(ast, solver.model(), end_time).copy()
    for i in range(end_time):
        debug(3, '---')
        old_command = test[i]
        replaced_whole_command: bool = False
        for x in range(2):
            new_command = command_dictionary.generate_random_dict_command()
            for field in ast.get_any_args():
                new_command[field] = old_command[field]
            test[i] = new_command
            if ast.evaluate(test):
                replaced_whole_command = True
                break
            else:
                debug(3, f'failed replacing {old_command} with {new_command}')
        if replaced_whole_command:
            debug(3, f'-- refinement step {i}: replacing {old_command} with {new_command}')
        else:
            debug(3, f'refinement step {i}: keeping {old_command}, rejecting {new_command}, now trying argument by argument')
            test[i] = old_command
            random_args = command_dictionary.generate_random_arguments_for_command(test[i]['name'])
            for arg_name, arg_value in random_args.items():
                if arg_name in ast.get_any_args():
                    debug(3, f'not replacing any-field {arg_name}')
                else:
                    old_value = test[i][arg_name]
                    test[i][arg_name] = arg_value
                    debug(3, f'refining {arg_name} from {old_value} to {arg_value} -> {test[i]}')
                    if not ast.evaluate(test):
                        debug(3, f'that did not work, restoring old value {old_value}')
                        test[i][arg_name] = old_value
                    else:
                        debug(3, 'that worked')
    if not ast.evaluate(test):
        raise AssertionError('Model not satisfiable as expected')
    if Options.DEBUG_LEVEL >= 1:
        print_test(test)
    return test


def generate_tests(spec: Optional[str] = None, test_suite_size: Optional[int] = None, test_size: Optional[int] = None) -> TestSuite:
    """Generates tests from XML files describing commands and their types.

    The specification is the concatenation of two specification files:
    1) the specification extracted from the specification file identified by
    the configuration file, or "" if not identified.
    2) the specification provided as argument, if provided, or "" if `None`.
    The test suite size and test size are extracted
    from the configuration file if `None`.

    The returned test is also stored in the file `testsuite.json`.

    :param spec: an optional specification of constraints.
    :param test_suite_size: an optional number indicating number of tests to generate.
    :param test_size: an optional number of commands to generate in each test.
    :return: the testsuite, a list of lists of dictionaries, each representing a command.
    """
    start_time = time.time()
    config_spec: str = ''
    spec_file = command_dictionary.spec_file
    if spec_file is not None:
        try:
            with open(spec_file, "r") as file:
                config_spec = file.read()
        except:
            raise ValueError(f"Specification file {spec_file} cannot be read or does not exist.")
    spec = config_spec + '\n\n' + (spec or '')
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
    if Options.PRINT_CONSTRAINTS:
        headline('FORMULA FROM SPEC ONLY')
        print(smt_ltl_formula)
    smt_formula: BoolRef = And(smt_rng_formula, smt_ltl_formula)
    tests: list[Test] = []
    for test_nr in range(test_suite_size):
        print(f"Generating test number {test_nr}")
        test = generate_test(ast, smt_formula, test_size)
        tests.append(test)
    for test_nr, test in enumerate(tests):
        print(f'\n=== test nr. {test_nr} ===\n')
        for cmd in test:
            print(cmd)
    print('\nWriting to file: fuzz-testsuite.json\n')
    with open('fuzz-testsuite.json', 'w') as file:
        json.dump(tests, file, indent=4)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.3f} seconds")
    return tests


def generate_test(ast: LTLSpec, smt_formula: BoolRef, end_time: int) -> Test:
    """Generates one test.

    :param ast: the specification of constraints.
    :param smt_formula: the formula as a Z3 datatype.
    :param end_time: the end time of the timeline.
    :return: the resulting test.
    """
    solver = Solver()
    if solve_formula(solver, smt_formula, end_time) is not None:
        if Options.PRINT_CONSTRAINTS:
            headline("ALL CONSTRAINTS")
            print(solver.assertions())
        extract_and_verify_test(ast, solver.model(), end_time)
        if Options.REFINEMENT_STRATEGY == RefinementStrategy.EVAL:
            test = refine_solver_using_evaluate(ast, solver, end_time)
        elif Options.REFINEMENT_STRATEGY == RefinementStrategy.EVAL_PER_ARG:
            test = refine_solver_using_evaluate_per_arg(ast, solver, end_time)
        else:
            test = refine_solver_using_to_smt(ast, solver, end_time)
        return test
    else:
        print("The specification must contain inconsistent constraints!")
        sys.exit(1)


def extract_and_verify_test(ast: LTLSpec, model: ModelRef, end_time: int) -> Test:
    """Extracts a test from a model.

    :param ast: the specification of constraints.
    :param model: the model to extract the test from.
    :param end_time: the end time of the timeline.
    :return: the resulting test.
    """
    test = [extract_command(model.eval(timeline(i)), model) for i in range(end_time)]
    if not ast.evaluate(test):
        error(f"*** generated test does not satisfy LTL semantics:\n {test}")
    return test


def verify_test(test: Test, spec: Optional[str] = None) -> bool:
    """Verifies that a test satisfies a specification.

    The specification is the concatenation of two specification files:
    1) the specification extracted from the specification file identified by
    the configuration file, or "" if not identified.
    2) the specification provided as argument, if provied, or "" if `None`.

    Note that the constraints provided in the XML command dictionary are not checked,
    only the specification.

    Note that the function parses the specification.

    :param test: the test to check against the specification.
    :param spec: an optional specification of constraints.
    :return: True iff. the test satisfies the specification.
    """
    config_spec: str = ''
    spec_file = command_dictionary.spec_file
    if spec_file is not None:
        try:
            with open(spec_file, "r") as file:
                config_spec = file.read()
        except:
            raise ValueError(f"Specification file {spec_file} cannot be read or does not exist.")
    spec = config_spec + '\n\n' + (spec or '')
    ast: LTLSpec = parse_spec(spec)
    return ast.evaluate(test)

