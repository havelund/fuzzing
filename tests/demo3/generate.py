
# FIT script:

import os
import json

def generate(version: str) -> list[list[dict]]:
    cmd = f'python{version} ...'
    os.system(cmd)
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data


generate('3.11')
