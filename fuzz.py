
"""
Module Name: fuzz.py
Description: This module provides the `fuzz` library functions `generate_tests` and
`print_tests`. It is defined at the top level in order to simplify import when
the `PYTHONPATH` approach is used to point to the top level `fuzzing` directory containing
this project. This allows a user to write e.g.:
`from fuzz import generate_tests, print_tests`
"""

from src.fuzz.fuzz import generate_tests, print_tests

