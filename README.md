
# fuzz
 
This repository contains a library `fuzz` for fuzz testing 
flight software. The main
function, `generate_tests`, provided by the library, generates a test suite,
which is a list of tests. Each test is a list of commands, which can be sent
to the flight software from a FIT script, either as a command list,
or one by one, as preferred. Each test is randomly generated, potentially 
restricted by user provided constraints.

The objective of fuzzing is to invoke unlikely, untried, command sequences on the flight
software in an attempt to break it.

`generate_tests` takes as input a description of possible commands in XML format, 
a description of what particular flight software modules should be tested (areas), 
and a configuration which guides how tests are generated.

```
+--------------------------------------------------+
|                The fuzz Module                   |
|                                                  |
|  +------------------+   +--------------------+   |
|  | commands + areas |   |    configuration   |   |
|  +--------+---------+   +---------+----------+   |
|           |                       |              |
|           V                       V              |
|        /-----------------------------\           |
|       |         generate_tests        |          |
|        \-----------------------------/           |
|                        |                         |
|                        V                         |
|  +-----------------------------------------+     |
|  |          list of generated tests        |     |
|  +-----------------------------------------+     |
+--------------------------------------------------+
```
A generated test suite is a list of tests, each being a list of commands,
each being represented as  a dictionary containing the name of the command and any arguments.
Here this is shown in schematic form with _m_ tests with _n_ commands in each test.

```
[
  [cmd_11, cmd_12, ...,cmd_1n],
  [cmd_21, cmd_22, ...,cmd_2n],
  
  [cmd_m1, cmd_m2, ...,cmd_mn],
]
```

Below is an example of a generated test suite consisting of two tests, each containing three commands.
The name of the command is denoted by `"name"`, and the rest of the fields in a command are the arguments,
in the order in which they must be provided (it is an ordered dictionary).

```python
[
    [
        {
            "name": "DDM_ENABLE_DWN_PB_EXIT_GATE",
            "dwn_framing_packet_buffer": "DIAGNOSTIC_EVR",
            "enable_disable": "ENABLE"
        },
        {
            "name": "GNC_SRU_SET_EXT_OH_REF_FRAME",
            "which_sru_eu": "NON_PRIME_SRU_EU",
            "which_sru_oh": "BOTH"
        },
        {
            "name": "GNC_SRU_READ_DIAG_DATA",
            "which_sru_eu": "SRU_EU_B"
        }
    ],
    [
        {
            "name": "DDM_CLOSE_OPEN_CONT_DP"
        },
        {
            "name": "DDM_DEL_DP",
            "apid": 268,
            "time_type": "DVT",
            "filter_time_start": 2262188308,
            "filter_time_end": 1622977556,
            "sent_status": "ALL"
        },
        {
            "name": "DDM_ENABLE_DWN_PB_EXIT_GATE",
            "dwn_framing_packet_buffer": "REALTIME_EHA_4",
            "enable_disable": "ENABLE"
        }
    ]
]
```

### Installation

The suggested approach is to install the library with `pip install` and then import and use it 
in a Python FTT module, as shown below.

#### Prerequisites

- Python 3.6 or higher installed on your system.
- A working installation of pip.

#### Obtain the Project

Clone or copy the fuzzing project to your local machine, say in:

```
/path/to/fuzzing/
```

#### Activate the Virtual Environment

Activate the pre-configured virtual environment 
provided with the project:

```
source /path/to/fuzzing/venv/bin/activate
```

#### Install the Package

```
cd /path/to/fuzzing
pip install -e .
```


## Usage

#### Create and/or Go to a New Directory

```
mkdir /path/to/testfuzz
cd /path/to/testfuzz
```

One may have to do this in that dirctory (not sure):

```
pip install /path/to/fuzzing
```

#### Create a Script, named e.g. `fit.py`:

```python
from fuzz import generate_tests, print_tests

path_to_xml = 'path/to/xml'
fsw_areas = ['area1', 'area2', 'area3']

tests = generate_tests(path_to_xml, fsw_areas)

print_tests(tests)  

# Example showing intended use:

for test in tests:
    print('=========')
    print('reset fsw')
    print('=========')    
    for cmd in test:
        print('---')
        print(f'send {cmd}')
```

The idea is that the FIT module walks through the generated tests and submit them to the flight software.

#### Run the Script

```
python fit.py
```

## The Functions in the `fuzz` library

### generate_test

```python
def generate_tests(fsw_dir: str, fsw_areas: List[str], config: Optional[Union[str,dict]] = None) -> List[List[dict]]:
```

Generates a test suite, which is a list of tests, each consisting of a list of commands.

It reads definitions of commands and their argument types, including enumerations,
from XML files stored in a given directory. It only generates commands for certain FSW areas,
provided as an argument as well. A configuration defines how many tests should be generated,
how many commands in each test, and constraints on what sequences of commands should be generated.

Parameters:
- fsw_dir: the directory containing command and enumeration descriptions in XML format.
- fsw_areas: the FSW areas commands should be generated for.
- config: configuration. If not provided, it is assumed that it is defined in a file
  named `config.json` stored in the same place the script is run. If provided, it can be
  provided in one of two forms: (1) as a string, which indicates the path to a `.json`
  file containing the configuration; (2) as a dictionary representing the configuration.

Returns
- the generated test suite, a list of tests, each being a list of commands.

### print_tests

```python
def print_tests(tests: List[List[dict]]):
```  
Pretty prints a generated test. A test can also be printed with just calling `print`. However, this will
result in all tests being printed on one line, which is difficult to read.

Parameter:

- tests: the test to be printed.

## Constraint Language

The configuration must have the following format (either as a `.json` file or as a dictionary):

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
      "cmd": str,
      "arg": str,
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
      "cmds": List[str]
    }
```

The `include` constraint restricts generated commands to a given subset.
Only those commands will be generated.

### Exclude

```json
    {
      "active": bool,
      "kind": "exclude",
      "cmds": List[str]
    }
```

The `exclude` constraint restricts generated commands to those not in 
a given subset. The command in the provided set will not be
generated.

### Followed_by

```json
    {
      "active": bool,
      "kind": "followed_by",
      "cmd1": str,
      "cmd2": str
    }
```

The `followed_by` constraint restricts tests to such where: if there is a 
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

### Followed_by_next

```json
    {
      "active": bool,
      "kind": "precedes_prev",
      "cmd1": str,
      "cmd2": str
    }
```

The `followed_by_next` constraint restricts tests to such where: if there is a 
`cmd1` in the test, it will be followed immediately after by a `cmd2` in the test.

### Precedes_prev

```json
    {
      "active": bool,
      "kind": "precedes_prev",
      "cmd1": str,
      "cmd2": str
    }
```

The `precedes_prev` constraint restricts tests to such where: if there is a 
`cmd2` in the test, it will be preceded immediately before in the test by a `cmd1` in the test.

### Eventually

```json
    {
      "active": bool,
      "kind": "eventually",
      "cmd": str
    }
```

The `eventually` constraint restricts tests to such where there is at least one 
`cmd` in the test.

### Example

Here is an example of a [config.json](https://github.jpl.nasa.gov/lars/fuzzing/blob/main/data/input/constraints/config.json) file.

### A Few Words on Constraints

#### Two Categories

The constraints above can be classified into two categories:

- _Command modifying constraints_: these include `range`, `include`, and `exclude`. These are applied immediately before
  test case generation begins, limiting the commands and their arguments. Such constraints are therefore very efficient.
- _Test verifying constraints_: these include the rest. These are applied after each test has been generated. If the generated test
  does not satisfy one of these constraints it is rejected (the number of rejected tests are printed out). This can therefore be
  ineffecient, depending on the constraints. The more constraining they are, the less likely it is that the random test generator
  will generate a test that satisfies them, resulting in more computation time, and in worst case non-termination.

#### Temporal Logic

Behind the scenes `fuzz` uses an advanced temporal logic with future and past time operators, and a so-called freeze operator enabling capturing data values in commands and relate them across commands. However, this temporal logic is currently not made available to
the user. At some point it will be.

#### Algorithm

As mentioned, the test case algorithm works by repeatedly generate a test randomly and then check whether it satisfies 
the constraints. A more efficient approach is if the two phases are merged. We are working on such an approach using
SMT solving using the [z3](https://github.com/Z3Prover/z3) SMT solver.

## Contributing

- Tracy Clark (348B)
- Klaus Havelund (348B)
- Vivek Reddy (348B)
