
# FSWfuzzer
 
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

## Constraint Language

The `fuzz.py` script takes as argument a configuration file which must have the 
following format:

```json
{
  "testsuite_size": int,
  "test_size": int,
  "constraints": [
    constraint_1,
    ...
    constraint_n
  ]
}
```

Each constraint must be one of the following kinds of objects.

### Range

```json
   {
      "active": bool,
      "kind": "range",
      "command": str,
      "argument": str,
      "range_min": int,
      "range_max": int
    }
```

The `range` constraint limits the range of a particular argument of
a particular command.

The `active` field indicates whether the constraint should be applied
(`true`) or not (`false`). It can be used to switch off or on constraints. If this field 
is not present, it is the same as `"active": true`. 

### Include

```json
    {
      "active": bool,
      "kind": "include",
      "commands": List[str]
    }
```

The `include` constraint restricts generated commands to a given subset.
Only those commands will be generated.

### Exclude

```json
    {
      "active": bool,
      "kind": "exclude",
      "commands": List[str]
    }
```

The `exclude` constraint restricts generated commands to those not in 
a given subset. The command in the provided set will not be
generated.

### Followedby

```json
    {
      "active": bool,
      "kind": "followedby",
      "cmd1": str,
      "cmd2": str
    }
```

The `followedby` constraint restricts tests to such where: if there is a 
`cmd1` in the test, it will be followed eventually by a `cmd2` in the test.
It is not one-to-one. That is, a single `cmd2` can match two `cmd1`s for example.

### Precedes

```json
    {
      "active": bool,
      "kind": "precedes",
      "cmd1": str,
      "cmd2": str
    }
```

The `precedes` constraint restricts tests to such where: if there is a 
`cmd2` in the test, it will be preceded earlier in the test by a `cmd1` in the test.
It is not one-to-one. That is, a single `cmd1` can match two `cmd2`s for example.

