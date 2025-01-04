
from src.fuzz.solver import *


def run(spec):
    test = generate_test_satisfying_formula(spec, end_time=10)
    print_test(test)


if __name__ == '__main__':
    spec = """
    norule p1: always FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x?) => 
        eventually FUZZ_CMD_MIXED_5(fuzz_cmd5_arg_5=x) 

    norule p2: eventually FUZZ_CMD_UNSIGNED_ARG_1()

    norule p3: eventually FUZZ_CMD_STRING_3()
    
    norule p4: eventually FUZZ_CMD_FLOAT_4()
    
    norule p5: count (9,9) FUZZ_CMD_ENUM_2(fuzz_cmd2_arg_1="fuzz_val_2")
    
    norule p6: eventually FUZZ_CMD_ENUM_2()
    
    norule p7: eventually FUZZ_CMD_UNSIGNED_ARG_1()    
    
    rule p8: always (FUZZ_CMD_UNSIGNED_ARG_1(fuzz_cmd1_arg_1=x?) => (x < 500))
    
    rule p9: always FUZZ_CMD_FLOAT_4()
    
    # FUZZ_CMD_UNSIGNED_ARG_1
    # FUZZ_CMD_ENUM_2
    """
    run(spec)

'''
==========
ENUM DICT:
==========
{'enable_disable': ['DISABLE', 'ENABLE'],
 'fuzz_enum_def1': ['fuzz_val_1', 'fuzz_val_2', 'fuzz_val_3']}
==========
CMD DICT:
==========
{'FUZZ_CMD_ENUM_2': {'args': [{'length': 8,
                               'name': 'fuzz_cmd2_arg_1',
                               'range_max': None,
                               'range_min': None,
                               'type': 'fuzz_enum_def1'},
                              {'length': 8,
                               'name': 'fuzz_cmd2_arg_2',
                               'range_max': None,
                               'range_min': None,
                               'type': 'enable_disable'}],
                     'opcode': '0x0002'},
 'FUZZ_CMD_FLOAT_4': {'args': [{'length': 64,
                                'name': 'fuzz_cmd4_arg_1',
                                'range_max': 1,
                                'range_min': -1,
                                'type': 'float_arg'},
                               {'length': 64,
                                'name': 'fuzz_cmd4_arg_2',
                                'range_max': 1,
                                'range_min': -1,
                                'type': 'float_arg'},
                               {'length': 64,
                                'name': 'fuzz_cmd4_arg_3',
                                'range_max': 1,
                                'range_min': -1,
                                'type': 'float_arg'}],
                      'opcode': '0x0004'},
 'FUZZ_CMD_MIXED_5': {'args': [{'length': 8,
                                'name': 'fuzz_cmd5_arg_1',
                                'range_max': None,
                                'range_min': None,
                                'type': 'fuzz_enum_def1'},
                               {'length': 8,
                                'name': 'fuzz_cmd5_arg_2',
                                'range_max': None,
                                'range_min': None,
                                'type': 'enable_disable'},
                               {'length': 32,
                                'name': 'fuzz_cmd5_arg_3',
                                'range_max': 2,
                                'range_min': -2,
                                'type': 'float_arg'},
                               {'length': 32,
                                'name': 'fuzz_cmd5_arg_4',
                                'range_max': 2,
                                'range_min': -2,
                                'type': 'float_arg'},
                               {'length': 32,
                                'name': 'fuzz_cmd5_arg_5',
                                'range_max': None,
                                'range_min': None,
                                'type': 'unsigned_arg'}],
                      'opcode': '0x0005'},
 'FUZZ_CMD_STRING_3': {'args': [{'length': 1024,
                                 'name': 'fuzz_cmd3_arg_1',
                                 'range_max': None,
                                 'range_min': None,
                                 'type': 'var_string_arg'},
                                {'length': 1024,
                                 'name': 'fuzz_cmd3_arg_2',
                                 'range_max': None,
                                 'range_min': None,
                                 'type': 'var_string_arg'}],
                       'opcode': '0x0003'},
 'FUZZ_CMD_UNSIGNED_ARG_1': {'args': [{'length': 32,
                                       'name': 'fuzz_cmd1_arg_1',
                                       'range_max': 800,
                                       'range_min': 1,
                                       'type': 'unsigned_arg'},
                                      {'length': 16,
                                       'name': 'fuzz_cmd1_arg_2',
                                       'range_max': 200,
                                       'range_min': 1,
                                       'type': 'unsigned_arg'},
                                      {'length': 8,
                                       'name': 'fuzz_cmd1_arg_3',
                                       'range_max': 10,
                                       'range_min': 1,
                                       'type': 'unsigned_arg'}],
                             'opcode': '0x0001'}}
'''