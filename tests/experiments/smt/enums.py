from z3 import *

SignalColor = Datatype('SignalColor')
SignalColor.declare('red')
SignalColor.declare('green')
SignalColor.declare('blue')
SignalColor = SignalColor.create()

AlarmColor = Datatype('AlarmColor')
AlarmColor.declare('red')
AlarmColor.declare('yellow')
AlarmColor.declare('green')
AlarmColor = AlarmColor.create()

Command = Datatype('Command')
Command.declare('SIGNAL', ('SIGNAL_time', IntSort()), ('SIGNAL_color', SignalColor))
Command.declare('ALARM',  ('ALARM_time', IntSort()), ('ALARM_color', AlarmColor))
Command = Command.create()

s = Solver()

c1 = Const('c1', Command)
c2 = Const('c2', Command)

cmd1 = Command.SIGNAL(1, SignalColor.red)

s.add(c1 == Command.SIGNAL(1, SignalColor.blue))
s.add(Command.is_ALARM(c2))
s.add(Command.ALARM_color(c2) == AlarmColor.red)

s.add(Command.ALARM_color(c2) == getattr(AlarmColor, "red"))
s.add(getattr(Command, "ALARM_color")(c2) == getattr(AlarmColor, "red"))


if __name__ == '__main__':
    if s.check() == sat:
        model = s.model()
        print(f"Solution found: {model}")
    else:
        print("No solution found.")