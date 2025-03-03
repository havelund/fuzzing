

from z3 import *

Command = Datatype('Command')

Command.declare('mk_move_cmd', ('mk_move_cmd_time', IntSort()), ('mk_move_cmd_number', IntSort()), ('mk_move_cmd_distance', IntSort()))
Command.declare('mk_align_cmd', ('mk_align_cmd_time', IntSort()), ('mk_align_cmd_number', IntSort()), ('mk_align_cmd_turn_angle', IntSort()))
Command.declare('mk_turn_cmd', ('mk_turn_cmd_time', IntSort()), ('mk_turn_cmd_number', IntSort()), ('mk_turn_cmd_turn_angle', IntSort()))
Command.declare('mk_cancel_cmd', ('mk_cancel_cmd_time', IntSort()), ('mk_cancel_cmd_number', IntSort()))
Command.declare('mk_stop_cmd', ('mk_stop_cmd_time', IntSort()), ('mk_stop_cmd_number', IntSort()))
Command.declare('mk_capture_cmd', ('mk_capture_cmd_time', IntSort()), ('mk_capture_cmd_number', IntSort()), ('mk_capture_cmd_images', IntSort()))
Command.declare('mk_send_cmd', ('mk_send_cmd_time', IntSort()), ('mk_send_cmd_number', IntSort()), ('mk_send_cmd_images', IntSort()))
Command.declare('mk_log_cmd', ('mk_log_cmd_time', IntSort()), ('mk_log_cmd_number', IntSort()), ('mk_log_cmd_data', IntSort()))

Command = Command.create()

timeline = Function('timeline', IntSort(), Command)


from z3 import *


def extract_command(command: Command, model: ModelRef) -> dict:
    """
    Extracts information from a Z3 Command datatype instance dynamically using
    the number of constructors and their fields.

    :param command: The Z3 Command datatype instance to extract data from.
    :param model: The Z3 model used to evaluate the values.
    :return: A dictionary containing the constructor name and field values.
    :raises ValueError: If the command does not match workingarea constructor.
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
                field_value = model.eval(field_selector(command)).as_long()
                simple_field_name = field_name[len(constructor_name) + 1:]
                data[simple_field_name] = field_value
            return data
    raise ValueError("Unknown command type")


if __name__ == '__main__':
    solver = Solver()

    cmd_instance = Command.mk_move_cmd(10, 2, 100)
    solver.add(timeline(0) == cmd_instance)

    if solver.check() == sat:
        model = solver.model()
        print(model)
        extracted = extract_command(timeline(0), model)
        print(extracted)