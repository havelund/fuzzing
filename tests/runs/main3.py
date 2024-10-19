
import fuzz

config_file = 'path/to/config.json'
fsw_path = 'path/to/dicts.xml'
fsw_areas = ["nav", "power"]

tests = fuzz.generate_testsuite(config_path, fsw_path, fsw_areas)

'''
So the question is whether we have to reset the configuation file constantly.
'''


