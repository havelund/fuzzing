
import json

if __name__ == '__main__':
    with open('fuzz-testsuite.json', 'r') as file: tests = json.load(file)
    for test in tests:
        print(f'RESET SUT')
        for cmd in test:
            print(cmd)
