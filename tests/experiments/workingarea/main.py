
"""
Working area!
"""

def find_fsw_command(cmd_name: str) -> FSWCommand:
    ...

def generate_random_arguments_for_command(cmd_name: str) -> dict:
    fsw_command: FSWCommand = find_fsw_command(cmd_name)
    return {arg.name: arg.random_python_value() for arg in fsw_command.arguments}

# ---

def generate_random_dict_command(self) -> dict:
    """generates a random Python command. Used for test refinement with just Python."""
    fsw_command: FSWCommand = random.choice(self.commands)
    command_name = {'name': fsw_command.name}
    arguments = {arg.name: arg.random_python_value() for arg in fsw_command.arguments}
    command = {**command_name, **arguments}
    return command


def refine_solver_using_evaluate(ast: LTLSpec, solver: Solver, end_time: int) -> Test:
    for i in range(end_time):
        old_command = test[i]
        test[i] = command_dictionary.generate_random_dict_command()
        if ast.evaluate(test):
            print(f'-- refinement step {i}: entire command changed=True')
        else:
            print(f'refinement step {i}: entire command changed=False, now trying argument by argument')
            test[i] = old_command
            random_args = generate_random_arguments_for_command(test[i]['name'])
            for arg_name, arg_value in random_args.items():
                old_value = test[i][arg_name]
                test[i][arg_name] = arg_value
                print(f'refining {arg_name} from {old_value} to {arg_value}')
                if not ast.evaluate(test):
                    print(f'that did not work, restoring old value {old_value}')
                    test[i][arg_name] = old_value
                else:
                    print('that worked')
