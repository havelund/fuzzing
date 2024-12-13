
from z3 import *
import random

"""
This file should be auto-generared from the XML command and enum
dictionaries. It is, however, not quite clear how this will work.
To be done.
"""


Command = Datatype('Command')
Command.declare('mk_move_cmd', ('move_speed', IntSort()))
Command.declare('mk_turn_cmd', ('turn_angle', IntSort()))
Command.declare('mk_cancel_cmd')
Command = Command.create()

timeline = Function('timeline', IntSort(), Command)


def generate_command() -> Command:
    random_choice = random.choice(['mk_move_cmd', 'mk_turn_cmd', 'mk_cancel_cmd'])
    if random_choice == 'mk_move_cmd':
        command = Command.mk_move_cmd(random.randint(0, 20))
    elif random_choice == 'mk_turn_cmd':
        command = Command.mk_turn_cmd(random.randint(0, 360))
    else:
        command = Command.mk_cancel_cmd
    return command


def extract_command(command: Command, model: ModelRef) -> dict:
    if model.eval(Command.is_mk_move_cmd(command)):
        name = 'MOVE'
        speed = model.eval(Command.move_speed(command)).as_long()
        return {'name': name, 'speed': speed}
    elif model.eval(Command.is_mk_turn_cmd(command)):
        name = 'TURN'
        angle = model.eval(Command.turn_angle(command)).as_long()
        return {'name': name, 'angle': angle}
    elif model.eval(Command.is_mk_cancel_cmd(command)):
        name = 'CANCEL'
        return {'name': name}
    else:
        assert False, f'SMT command {command} not recognized'

