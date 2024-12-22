
from z3 import *
import random

"""
This file should be auto-generared from the XML command and enum
dictionaries. It is, however, not quite clear how this will work.
To be done.
"""


Command = Datatype('Command')

Command.declare('mk_move_cmd', ('time', IntSort()), ('number', IntSort()), ('distance', IntSort()))
Command.declare('mk_align_cmd', ('time', IntSort()), ('number', IntSort()), ('turn_angle', IntSort()))
Command.declare('mk_turn_cmd', ('time', IntSort()), ('number', IntSort()), ('turn_angle', IntSort()))
Command.declare('mk_cancel_cmd', ('time', IntSort()), ('number', IntSort()))
Command.declare('mk_stop_cmd', ('time', IntSort()), ('number', IntSort()))
Command.declare('mk_capture_cmd', ('time', IntSort()), ('number', IntSort()), ('images', IntSort()))
Command.declare('mk_send_cmd', ('time', IntSort()), ('number', IntSort()), ('images', IntSort()))
Command.declare('mk_log_cmd', ('time', IntSort()), ('number', IntSort()), ('data', IntSort()))

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
    if model.eval(Command.is_mk_move_cmd(command)):
        name = 'mk_move_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        distance = model.eval(Command.distance(command)).as_long()
        return {'name': name, 'time': time, 'number': number, 'distance': distance}
    elif model.eval(Command.is_mk_align_cmd(command)):
        name = 'mk_align_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        angle = model.eval(Command.turn_angle(command)).as_long()
        return {'name': name, 'time': time, 'number': number, 'turn_angle': angle}
    elif model.eval(Command.is_mk_turn_cmd(command)):
        name = 'mk_turn_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        angle = model.eval(Command.turn_angle(command)).as_long()
        return {'name': name, 'time': time, 'number': number, 'turn_angle': angle}
    elif model.eval(Command.is_mk_cancel_cmd(command)):
        name = 'mk_cancel_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        return {'name': name, 'time': time, 'number': number}
    elif model.eval(Command.is_mk_stop_cmd(command)):
        name = 'mk_stop_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        return {'name': name, 'time': time, 'number': number}
    elif model.eval(Command.is_mk_capture_cmd(command)):
        name = 'mk_capture_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        images = model.eval(Command.images(command)).as_long()
        return {'name': name, 'time': time, 'number': number, 'images': images}
    elif model.eval(Command.is_mk_send_cmd(command)):
        name = 'mk_send_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        images = model.eval(Command.images(command)).as_long()
        return {'name': name, 'time': time, 'number': number, 'images': images}
    elif model.eval(Command.is_mk_log_cmd(command)):
        name = 'mk_log_cmd'
        time = model.eval(Command.time(command)).as_long()
        number = model.eval(Command.number(command)).as_long()
        data = model.eval(Command.data(command)).as_long()
        return {'name': name, 'time': time, 'number': number, 'data': data}
    else:
        assert False, f'SMT command {command} not recognized'

