from z3 import *

num_steps = 5

commands = [{'name': Int(f'name_{i}'), 'speed': Int(f'speed_{i}')} for i in range(num_steps)]

solver = Solver()

eventually_move_fast = Or([And(commands[i]['name'] == 1, commands[i]['speed'] > 10) for i in range(num_steps)])

solver.add(eventually_move_fast)

for i in range(num_steps):
    solver.add(Or(commands[i]['name'] == 1, commands[i]['name'] == 2))
    solver.add(commands[i]['speed'] >= 0)

if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    for i in range(num_steps):
        print(f"Command {i}: name = {model[commands[i]['name']]}, speed = {model[commands[i]['speed']]}")
else:
    print("No solution found.")


if __name__ == '__main__':
    pass

