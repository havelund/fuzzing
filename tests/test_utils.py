
from fuzz import *


TEST_SUITE_SIZE = 1
# TEST_SIZE = 10
TEST_SIZE = 10


def norun(spec, refinement_strategy: int = 0):
    pass


def run(spec, refinement_strategy: int = 0):
    if refinement_strategy == 0:
        print('Refinement using to_smt')
        run_test(spec, RefinementStrategy.SMT)
        print('Refinement using evaluate')
        run_test(spec, RefinementStrategy.EVAL)
        print('Refinement using evaluate per arg')
        run_test(spec, RefinementStrategy.EVAL_PER_ARG)
    elif refinement_strategy == 1:
        print('Refinement using to_smt')
        run_test(spec, RefinementStrategy.SMT)
    elif refinement_strategy == 2:
        print('Refinement using evaluate')
        run_test(spec, RefinementStrategy.EVAL)
    elif refinement_strategy == 3:
        print('Refinement using evaluate per arg')
        run_test(spec, RefinementStrategy.EVAL_PER_ARG)



def run_test(spec, refinement_strategy: RefinementStrategy):
    old_strategy: RefinementStrategy = Options.REFINEMENT_STRATEGY
    Options.REFINEMENT_STRATEGY = refinement_strategy
    tests = generate_tests(spec, test_suite_size=TEST_SUITE_SIZE, test_size=TEST_SIZE)
    # print_tests(tests)
    Options.REFINEMENT_STRATEGY = old_strategy