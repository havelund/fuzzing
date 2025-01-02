from typing import Optional
import random

from src.fuzz.ltl_grammar import *
from src.fuzz.utils import debug


def print_model(model: ModelRef, end_time: int):
    print("===============")
    print("Solution found!")
    print("===============")
    for i in range(end_time):
        cmd = model.eval(timeline(i))
        print(f'{i:3}: {cmd}')
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
            for j in range(Command.constructor(i).arity()):
                field_selector = Command.accessor(i, j)
                field_name = field_selector.name()
                field_value = model.eval(field_selector(command)) # .as_long()
                simple_field_name = field_name[len(constructor_name) + 1:]
                data[simple_field_name] = field_value
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


def refine_solver(solver: Solver, end_time: int) -> ModelRef:
    for i in range(end_time):
        solver.push()

        command = command_dictionary.generate_command()
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


def generate_test_satisfying_formula(spec: str, end_time: int) -> Test:
    ast: LTLSpec = parse_spec(spec)
    smt_formula: BoolRef = ast.to_smt(end_time)
    solver = Solver()
    if solve_formula(solver, smt_formula, end_time) is not None:
        model = refine_solver(solver, end_time)
        test = [extract_command(model.eval(timeline(i)), model) for i in range(end_time)]
        print('checking generated test against semantics')
        assert ast.evaluate(test), f"*** generated test does not satisfy LTL semantics:\n {test}"
        return test
    else:
        sys.exit(1)

