
from z3 import *
import random

from src.fuzz.utils import debug

"""
This file should be auto-generared from the XML command and enum
dictionaries. It is, however, not quite clear how this will work.
To be done.
"""


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


def generate_command() -> Command:
    random_choice = random.choice(['mk_move_cmd', 'mk_turn_cmd', 'mk_cancel_cmd', 'mk_stop_cmd'])
    if random_choice == 'mk_move_cmd':
        command = Command.mk_move_cmd(random.randint(0, 2000), random.randint(0, 2000), random.randint(0, 20))
    elif random_choice == 'mk_align_cmd':
        command = Command.mk_align_cmd(random.randint(0, 2000), random.randint(0, 2000), random.randint(0, 360))
    elif random_choice == 'mk_turn_cmd':
        command = Command.mk_turn_cmd(random.randint(0, 2000), random.randint(0, 2000), random.randint(0, 360))
    elif random_choice == 'mk_stop_cmd':
        command = Command.mk_stop_cmd(random.randint(0, 2000), random.randint(0, 2000))
    elif random_choice == 'mk_cancel_cmd':
        command = Command.mk_cancel_cmd(random.randint(0, 2000), random.randint(0, 2000))
    elif random_choice == 'mk_capture_cmd':
        command = Command.mk_capture_cmd(random.randint(0, 2000), random.randint(0, 2000), random.randint(1, 10))
    elif random_choice == 'mk_send_cmd':
        command = Command.mk_send_cmd(random.randint(0, 2000), random.randint(0, 2000), random.randint(1, 10))
    elif random_choice == 'mk_log_cmd':
        command = Command.mk_log_cmd(random.randint(0, 2000), random.randint(0, 2000), random.randint(1, 2000))
    else:
        assert False, f"command {random_choice} not recognized"
    return command


def extract_command(command: Command, model: ModelRef) -> dict:
    constructors = [
        ("mk_move_cmd", ["time", "number", "distance"]),
        ("mk_align_cmd", ["time", "number", "turn_angle"]),
        ("mk_turn_cmd", ["time", "number", "turn_angle"]),
        ("mk_cancel_cmd", ["time", "number"]),
        ("mk_stop_cmd", ["time", "number"]),
        ("mk_capture_cmd", ["time", "number", "images"]),
        ("mk_send_cmd", ["time", "number", "images"]),
        ("mk_log_cmd", ["time", "number", "data"]),
    ]
    for cons, fields in constructors:
        if model.eval(getattr(Command, f"is_{cons}")(command)):
            data = {'name': cons}
            for field in fields:
                field_name = f"{cons}_{field}"
                data[field] = model.eval(getattr(Command, field_name)(command)).as_long()
            return data
    raise ValueError("Unknown command type")
