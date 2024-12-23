
from fuzz import generate_tests, print_tests

path_to_fsw = 'fsw'
fsw_areas = ['dwn']

tests = generate_tests(path_to_fsw, fsw_areas)

print_tests(tests)  

# Example showing intended use:

for test in tests:
    print('=========')
    print('reset fsw')
    print('=========')    
    for cmd in test:
        print(f'send {cmd}')


