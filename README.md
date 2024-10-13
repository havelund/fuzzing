
# LogicFuzz
 
This repository contains a framework for fuzz testing 
commands. 

## Organization of Repository

Current snapshot:

- data (_inputs to and outputs from running scripts_)
  - input
    - clipper1 (_example Europa Clipper input modules_)
    - tests
  - output (_for example test suites_)
    - testsuite_baseline.json
- material (_various material such as images, papers, ..._)
  - papers
  - ...
- src (_the tool itself represented as a collection of scripts_)
  - autogen_cmds.py (_conversion from enum and cmd dicts in XML to Python modules_)
  - cmds_to_json.py (_conversion from enum and cmd dicts in Python modules to Json_)
  - fuzzing (_generation of test suite_)
    - fuzz.py (_main script_)
    - core.py (_core functionality_)
    - temporal_logic.py (_abstract syntax and semantics for temporal logic_)
    - utils.py (_utilities_)
- tests
  - runs (_a collection of runs, not part of testing_)
  - test1.py (_a test_)
  - test2.py (_a test_)
  - ...
  - testutils.py (_test utilities_)
- zigzag (_various fuzzing experiments_)
  - grammars (_generating tests from a grammar_)
  - smt (_generating tests using the Z3 SMT solver_)

## Design

See wiki for discussion of design space.


