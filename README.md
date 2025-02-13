# fuzz

**THIS PAGE IS UNDER (RE)CONSTRUCTION**

**Version**: 2.0.0

## Introduction

This repository contains a library `fuzz` for fuzz testing
flight software. The main function, `generate_tests`, provided by the library, generates a test suite,
which is a list of tests. Each test is a list of commands, which can be sent
to the flight software from a FIT script, either as a command list,
or one by one, as preferred. Each test is randomly generated, potentially
restricted by user provided constraints.

The objective of fuzzing is to invoke unlikely, untried, command sequences on the flight
software in an attempt to break it.

`generate_tests` takes as input a description of possible commands in XML format,
a description of what particular flight software modules should be tested (areas),
and an optinal specification of constraints, which limits the amount of randomness,
thereby avoiding completely unrealistic command sequences. Tests are generated using
a constraint solver ([z3](https://github.com/Z3Prover/z3)).

```
+--------------------------------------------------+
|                The fuzz Module                   |
|                                                  |
|  +------------------+   +--------------------+   |
|  | commands + areas |   |    constraints     |   |
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
  [cmd_11, cmd_12, ...,cmd_1n], <--- test number 1 containing n commands
  [cmd_21, cmd_22, ...,cmd_2n], <--- test number 2 containing n commands
  
  [cmd_m1, cmd_m2, ...,cmd_mn], <--- test number m containing n commands
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

## Installation

### Prerequisites

- Python 3.6 or higher installed on your system.

### Obtain the Project

Clone or copy the fuzzing project to your local machine, say in:

```
/path/to/fuzzing/
```

### Installation Using The PYTHONPATH Approach

Set the PYTHONPATH environment variable to include this path, as example:

```bash
export PYTHONPATH=/path/to/fuzzing:$PYTHONPATH
```

Install Dependencies: `fuzz` uses a few packages that must be installed, if not already installed.
These can be installed e.g. with pip as follows:

```
pip install dotmap
pip install future
pip install z3-solver
```

### Installation Using the PIP INSTALL Approach

Execute the following command:

```
pip install /path/to/fuzzing
```

This will install `fuzz` with all its dependencies.

Note that if you want to install it in a virtual environment of a project, you
must first create this project (the steps below) and activate the virtual environment,
as described in [here](README-PACKAGING.md) before executing the above command.

## Usage

A demo example is shown in [src/tests/demo](https://github.jpl.nasa.gov/lars/fuzzing/tree/main/tests/demo2), which is explained below.
When having installed `fuzz` you can go to the folder containing the demo:

```
cd fuzzing/tests/demo2
```

```json
{
    "fsw_path": "fsw",
    "fsw_areas": ["mov"],
    "spec_path": "spec.txt",
    "test_suite_size": 10,
    "test_size": 10
}
```

## The Command and Enumeration XML Dictionaries

The first argument to the `generate_tests` function is a path to the flight software, where
XML files describing commands and enumeration types of command arguments are described.

Let's first describe the commands of our made up example at a high informal level of abstraction:

```python
types
    speed = {"slow", "medium", "fast"}
    image_quality = {"low", "high"}

commands
    MOVE(time:uint[0:1000], number:uint[0,100], distance:uint[1,100], speed:uint[1,10], message:string[10])
    ALIGN(time:uint[0:1000], number:uint[0,100], degrees:float[0,360], message:string[10])
    TURN(time:uint[0:1000], number:uint[0,100], angle:float[-180,180], message:string[10])
    CANCEL(time:uint[0:1000], number:uint[0,100], message:string[10])
    STOP(time:uint[0:1000], number:uint[0,100], message:string[10])
    PIC(time:uint[0:1000], number:uint[0,100], images:uint[1,10], quality:image_quality, message:string[10])
    SEND(time:uint[0:1000], number:uint[0,100], images:uint[1,100], message:string[10])   
    LOG(time:uint[0:1000], number:uint[0,100], message:string[10])
```

Each command carries a time stamp and a command number. Types are indicated as (unsigned) `uint`, `float`, 'string',
or the name of an enumerated type, e.g. `image_quality`. For numeric types a range is indicated with lower and upper bound
between square brackets. For strings the length is indicated between square brackets. 

The command set offers commands for moving (`MOVE`) a rover, 
aligning (`ALIGN`) the rover to face in a particular absolute direction, 
turning (`TURN`) the rover a relative number of degrees,
cancel (`CANCEL`) a command,
stop (`STOP`) a driving,
take a picture (`PIC`),
send (`SEND`) pictures to ground,
log (`LOG`) data.

The structure of the flight software directory is assumed to be the following:

```
fsw
  |__ src
        |___ aaa_xxx
        |    |___ aaa_xxx_ai_cmd.xml
        |
        |____aaa_yyy
        |    |___ aaa_yyy_ai_cmd.xml
        |
        |___ bbb_xxx
        |    |___ bbb_xxx_ai_cmd.xml
        |
        |____bbb_yyy
        |    |___ bbb_yyy_ai_cmd.xml 
        |
        |___ ccc_xxx
        |    |___ ccc_xxx_ai_cmd.xml
        |
        |____ccc_yyy
             |___ ccc_yyy_ai_cmd.xml  
```

Where `aaa`, `bbb`, and `ccc` are areas, and
where `xxx`, `yyy`, `zzz` is each one of `mgr`, `ctl`, `svc`, `exe`, and `ptm`.
In our case, the `fsw` folder has the following structure:

```
fsw
  |__ src
        |___ mov_mgr
             |___ mov_mgr_ai_cmd.xml
```


Each of the XML files have the following format, defining an entry of enumeration
types and an entry of command definitions, with arguments having types which include
the enumeration types:

```xml
<command_dictionary>
  
    <enum_definitions>
       ... 
    </enum_definitions>

    <command_definitions>
       ...   
    </command_definitions>

</command_dictionary>
```

A complete but made up example is shown below:

```xml
<command_dictionary>
        <header mission_name="FUZZ_MISSION" schema_version="1.0" version="10.1.0.2">
        </header>

        <enum_definitions>

          <enum_table name="speed">
            <values>
              <enum numeric="0" symbol="slow"/>
              <enum numeric="1" symbol="medium"/>
              <enum numeric="2" symbol="fast"/>
            </values>
          </enum_table>

          <enum_table name="image_quality">
            <values>
              <enum numeric="0" symbol="low"/>
              <enum numeric="1" symbol="high"/>
            </values>
          </enum_table>

        </enum_definitions>

        <command_definitions>

          <fsw_command class="FSW" opcode="0x0001" stem="MOVE">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="distance" units="meters">
                <range_of_values>
                  <include max="100" min="1"/>
                </range_of_values>
                <description>The distance to move.</description>
              </unsigned_arg>

              <float_arg bit_length="64" name="speed" units="m/h">
                <range_of_values>
                  <include max="10" min="1"/>
                </range_of_values>
                <description>The speed</description>
              </float_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>

            <description>Move command.</description>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0002" stem="ALIGN">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <float_arg bit_length="64" name="angle" units="degrees">
                <range_of_values>
                  <include max="180" min="-180"/>
                </range_of_values>
                <description>Degree to turn.</description>
              </float_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0003" stem="TURN">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <float_arg bit_length="64" name="angle" units="degrees">
                <range_of_values>
                  <include max="180" min="-180"/>
                </range_of_values>
                <description>Degree to turn.</description>
              </float_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0004" stem="CANCEL">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0005" stem="STOP">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0006" stem="PIC">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="images">
                <range_of_values>
                  <include max="10" min="1"/>
                </range_of_values>
                <description>Number of images to take.</description>
              </unsigned_arg>

              <enum_arg bit_length="8" enum_name="image_quality" name="quality">
                <description>Image quality.</description>
              </enum_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0007" stem="SEND">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="images">
                <range_of_values>
                  <include max="100" min="1"/>
                </range_of_values>
                <description>Number of images to send.</description>
              </unsigned_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>
          </fsw_command>

          <fsw_command class="FSW" opcode="0x0008" stem="LOG">
            <arguments>

              <unsigned_arg bit_length="32" name="time" units="seconds">
                <range_of_values>
                  <include max="1000" min="0"/>
                </range_of_values>
                <description>The current time.</description>
              </unsigned_arg>

              <unsigned_arg bit_length="32" name="number">
                <range_of_values>
                  <include max="100" min="0"/>
                </range_of_values>
                <description>Command number.</description>
              </unsigned_arg>

              <var_string_arg max_bit_length="10" name="message" prefix_bit_length="8">
                <description>Message</description>
              </var_string_arg>

            </arguments>
          </fsw_command>

        </command_definitions>

</command_dictionary>
```

### The Test Script

The folder contains the following script `fit.py`, which underneath reads in the XML 
command dictionary, specifies constraints as a text string, 
calls the `generate_tests` function with the specification as argument,
as well as indicating how many tests to generate (`test_suite_size`) and how many commands in each 
test (`test_size`).

```python
from src.fuzz import generate_tests

spec = """
    rule stop:
      always MOVE(number=n?) => eventually STOP(number=n)

    rule one_align: count 2 ALIGN()
    
    rule two_three_turns: count (2,3) TURN()
    
    rule limit_degree:
      always TURN(angle=a?) => -10 <= a <= 10
        
    rule align_followed_by_turn: 
      always ALIGN(angle=a?) => next ! ALIGN(angle=a) until MOVE()
    """


if __name__ == '__main__':
    tests: list[dict[str, object]] = generate_tests(spec, test_suite_size=2, test_size=10)
    for test in tests:
        print('=========')
        print('reset fsw')
        print('=========')
        for cmd in test:
            print(f'send {cmd}')
```

The script first generates the tests, storing them in the `tests` file as a list of dictionaries, each representing a test.
At this point it is up to the script writer how to use the tests. We here go through each test in a `for` loop, and for each 
command we print it out. For testing purposes, we would here submit the command to the SUT.

If the `spec` was empty (`spec = ""`), `generate_tests` will generate completely random commands, although respecting the minimal
and maximal bounds provided in the XML command dictionary. In the case above we have provided a non-empty specification
consisting of five constraints, all of which a test (command sequence) must satisfy. The language in which these constraints
is a temporal logic, which will be explained in detail below. Here we provide a quick explanation of the five
properties.

- **stop**: This property, named `stop`, states that it is always the case (for every position in the test), that if the command in that
position is a `MOVE` command with a `number` field which we **bind** (indicated ny `?`) to `n`, then eventually
later in the test there should be a `STOP` command with the `number` field being `n`. 

- **one_align**: This property states that there should be exactly two `ALIGN` commands, and we don't care about the arguments (in this constraint).

- **two_three_turns**: This property states that there should be between two or three `TURN` commands, and we don't care about the arguments (in this constraint).

- **limit_degree**: This property states that every `TURN` command should have an `angle`, which is bound to `a`, which is in
the interval -10 and 10.

- **align_followed_by_turn**: This property is slightly more complicated. It states that it is always the case, that if there is an
`ALIGN` command with an angle `a', then from the `next` position in the test, there is no `ALIGN` command
with the same angle `a`, `until` a `MOVE` command occurs, and it has to occur.


### Run the Script

```
python fit.py
```

Running this script yields the following:

```
=== reset fsw ===

send {'name': 'ALIGN', 'time': 55, 'number': 16, 'angle': -1.0, 'message': ''}
send {'name': 'ALIGN', 'time': 164, 'number': 23, 'angle': 0.0, 'message': ''}
send {'name': 'MOVE', 'time': 123, 'number': 92, 'distance': 96, 'speed': 1.0, 'message': ''}
send {'name': 'STOP', 'time': 587, 'number': 92, 'message': ''}
send {'name': 'TURN', 'time': 16, 'number': 94, 'angle': -2.0, 'message': ''}
send {'name': 'TURN', 'time': 927, 'number': 99, 'angle': 4.0, 'message': ''}
send {'name': 'PIC', 'time': 802, 'number': 1, 'images': 5, 'quality': 'low', 'message': ''}
send {'name': 'PIC', 'time': 652, 'number': 27, 'images': 9, 'quality': 'low', 'message': ''}
send {'name': 'CANCEL', 'time': 684, 'number': 8, 'message': ''}
send {'name': 'CANCEL', 'time': 552, 'number': 100, 'message': 'AeUWnNG8pN'}

=== reset fsw ===

send {'name': 'ALIGN', 'time': 277, 'number': 65, 'angle': -1.0, 'message': ''}
send {'name': 'ALIGN', 'time': 369, 'number': 91, 'angle': -115.04129160719944, 'message': '1Pcr9mECX4'}
send {'name': 'MOVE', 'time': 664, 'number': 92, 'distance': 66, 'speed': 1.0, 'message': ''}
send {'name': 'STOP', 'time': 802, 'number': 92, 'message': ''}
send {'name': 'TURN', 'time': 209, 'number': 15, 'angle': 0.0, 'message': ''}
send {'name': 'TURN', 'time': 474, 'number': 74, 'angle': 9.0, 'message': ''}
send {'name': 'PIC', 'time': 652, 'number': 38, 'images': 4, 'quality': 'low', 'message': ''}
send {'name': 'PIC', 'time': 565, 'number': 60, 'images': 6, 'quality': 'low', 'message': ''}
send {'name': 'CANCEL', 'time': 731, 'number': 23, 'message': ''}
send {'name': 'CANCEL', 'time': 723, 'number': 46, 'message': ''}
```

The reader can try and convince him or herself, that each of these two tests satisfies the constraints.

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

### General Introduction to Temporal Logic

The constraint language is a temporal logic with future and past time
operators, and which enables capturing values of command arguments in
one part of a formula, and refer to them  in another part of the formula.
The temporal logic is given a semantics such that for a given test _t_ and formula
_F_, the test satisfies the formula or not. We write:

```
           t |= F
```

to indicate that the trace _t_ satisfies the formula _F_.
As an example, consider the test _t_ (from our previous example):

```
[
  {'name': 'ALIGN', 'time': 55, 'number': 16, 'angle': -1.0, 'message': ''},
  {'name': 'ALIGN', 'time': 164, 'number': 23, 'angle': 0.0, 'message': ''},
  {'name': 'MOVE', 'time': 123, 'number': 92, 'distance': 96, 'speed': 1.0, 'message': ''},
  {'name': 'STOP', 'time': 587, 'number': 92, 'message': ''},
  {'name': 'TURN', 'time': 16, 'number': 94, 'angle': -2.0, 'message': ''},
  {'name': 'TURN', 'time': 927, 'number': 99, 'angle': 4.0, 'message': ''},
  {'name': 'PIC', 'time': 802, 'number': 1, 'images': 5, 'quality': 'low', 'message': ''},
  {'name': 'PIC', 'time': 652, 'number': 27, 'images': 9, 'quality': 'low', 'message': ''},
  {'name': 'CANCEL', 'time': 684, 'number': 8, 'message': ''},
  {'name': 'CANCEL', 'time': 552, 'number': 100, 'message': 'AeUWnNG8pN'}
]
```

This test satisfies for example the formula 
`always MOVE(number=n?) => eventually STOP(number=n)` and we write this as:

Our logic thus can be used to verify that a test satisfies a formula.
Turning this around, a formula can be used to **generate** a test that
satisfies the formula, and this is the game we are plying here. In fact,
we play both games: we can verify that a test satisfiles a formula, and we can
generate a test from a formula that satisfies the formula.

A temporal formula contains operators, such as `always` and
`eventually`, which refer to positions in the test.
For example a test satisfies `always F` if F is true in every 
single position of the test. A test satisfies `eventually F` if `F`
is true at some point in the future.

It is important to note that a formula is evaluated on a trace **and** a current
position _i_ in the trace, which we write as:

```
           t,i |= F
```

The whole test satisfies _F_ if

```
           t,0 |= F
```

which we abbreviate as:

```
           t |= F
```

### Detailed Explanation of Formulas

A specification has the form, where F1, F2, ..., are formulas:

```python
rule name1 : F1
rule name2 : F2
...
rule nameN : FN
```

The following table show the allowed formulas.

#### Capturing Commands and their Arguments

|      Formula       | Explanation                                                                                   |
|:------------------:|-----------------------------------------------------------------------------------------------|
|   ID(c1,...,cn)    | The current command has the name ID and has arguments that satisfy the constraints c1,...,cn. |
| ID(c1,...,cn) => F | If the current command matches ID(c1,...cn) then the formula F must be satisfied.             |
| ID(c1,...,cn) &> F | The current command matches ID(c1,...cn) and the formula F is satisfied.                      |

The constraints c1,...,cn can constrain the arguments, but they can also bind parameter values, which can then be
referred to in F. There are four kinds of constraints, each consraining a field, named f, of the command:

- f = x      : f must have the same value as the variable x introduced by one of the patterns above,
- f = x?     : f's value is bound to x and is now visible in the formula following => and &> above.
- f = 42     : f must be a number and have the value 42 in this case.
- f = "hot"  : f must be a string or an enumerayed type and have the value "hot".


#### Boolean Logic Operators


|     Formula      | Explanation                                                                                 |
|:----------------:|---------------------------------------------------------------------------------------------|
|      `true`      | The true formula.                                                                           |
|     `false`      | The false formula.                                                                          |
|     `not` F      | True if and only if F is false.                                                             |
|    F `and` G     | F and G.                                                                                    |
|     F `or` G     | F or G.                                                                                     |
|  F `implies` G   | F implies G.                                                                                |
|       (F)        | True if and only if F is true.                                                              |
|     e1 op e2     | For op being one of: <, <=, =, !=, >, >=. A relation between the values of two expressions. |
| e1 op1 e2 op2 e3 | Equivalent to: (e1 op1 e2) and (e2 op2 e3).                                                 |

An expression can be an identifier (e.g. x) introduced elsewhere in the formula, 
a number (e.g. -4 or 42), or a string (e.g. "hot").

#### Future Time Temporal Logic Operators

|    Formula     | Explanation                                                                                                        |
|:--------------:|--------------------------------------------------------------------------------------------------------------------|
|   `always` F   | F is true now and in in all future positions.                                                                      |
| `eventually` F | F is true now or in some future position.                                                                          |
|    `next` F    | F is true in the next position.                                                                                    |
|   `wnext` F    | F is true in the next position, if there is a next position (weak next)                                            |
|  F `until` G   | G is true now or in some future position _i_, and for all positions __j_ < _i__ until then F is true               |
|  F `wuntil` G  | G is true now or in some future position _i_, and for all positions __j_ < _i__ until then F is true, or always F. |

#### Past Time Temporal Logic Operators

|    Formula     | Explanation                                                                                                      |
|:--------------:|------------------------------------------------------------------------------------------------------------------|
|   `sofar` F    | F is true now and in in all past positions.                                                                      |
|    `once` F    | F is true now or in some past position.                                                                          |
|    `prev` F    | F is true in the previous position.                                                                              |
|   `wprev` F    | F is true in the previous position, if there is a previous position                                              |
|  F `since` G   | G is true now or in some past position _i_, and for all positions __j_ > _i__ since then F is true               |
|  F `wsince` G  | G is true now or in some past position _i_, and for all positions __j_ > _i__ since then F is true, or always F. |

#### Other Temporal Logic Operators

|            Formula            | Explanation                                                                                                                                                             |
|:-----------------------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|         `count` n  F          | F is true now and in in all past positions.                                                                                                                             |
|       `count` (n1,n2) F       | F is true now or in some past position.                                                                                                                                 |
|        `countpast` n F        | F is true in the previous position.                                                                                                                                     |
|     `countpast` (n1,n2) F     | F is true in the previous position, if there is a previous position (weak prev), which is not the case for the first postion                                            |
|          F `then` G           | G is true now or in some past position _i_, and for all positions __j_ > _i__ since then F is true                                                                      |
|          F `after` G          | G is true now or in some past position _i_, and for all positions __j_ > _i__ since then F is true, or (weak since) G never was true, and F is true always in the past. |

### Grammar

```python

<spec>::= <rule>*

<rule> ::= RULE ID ":" <formula>

<formula> ::= 
          <formula> IMPLIES <formula>  
        | ID "(" <constraints>? ")" (IFTHEN | ANDTHEN) <formula>
        | <formula> OR <formula>
        | <formula> AND <formula> 
        | ID "(" <constraints>? ")" 
        | ALWAYS <formula>
        | EVENTUALLY <formula> 
        | <formula> UNTIL <formula>
        | <formula> WUNTIL <formula>
        | <formula> SINCE <formula>
        | <formula> WSINCE <formula>
        | SOFAR <formula> 
        | ONCE <formula>
        | NEXT <formula>
        | WNEXT <formula> 
        | PREV <formula>  
        | WPREV <formula>  
        | NOT <formula> 
        | <expression> RELOP <expression>
        | <expression> RELOP <expression> RELOP <expression>
        | "(" <formula> ")"
        | "true"
        | "false"
        | COUNT "(" NUMBER "," NUMBER ")" <formula>
        | COUNTPAST   "(" NUMBER "," NUMBER ")" <formula>
        | COUNT NUMBER  <formula> 
        | COUNTPAST NUMBER <formula>
        | <formula THEN <formula>
        | <formula AFTER <formula>
        
<expression> ::= ID | NUMBER | STRING

<constraints> ::= <constraint> ("," <constraint>)*

<constraint> ::= 
            ID "=" ID
          | ID "=" ID "?" 
          | ID "=" NUMBER 
          | ID "=" STRING
```



| Token      | Syntax            |
|------------|-------------------|
|  `RULE`    | rule          , norule |
| `NOT`      | not           , ! |
| `IMPLIES`  | implies       , -> |
| `OR`       | or            , \| |
| `AND`      | and           , & |
| `ALWAYS`   | always        , [] |
| `EVENTUALLY` | eventually  , <>  |
| `UNTIL`    | until         , U |
| `WUNTIL`   | wuntil        , WU |
| `NEXT`     | next          , () |
| `WNEXT`    | wnext         , ()? |
| `SOFAR`    | sofar         , [*] |
| `ONCE`     | once          , <*> |
| `SINCE`    | since         , S |
| `WSINCE`   | wsince        , WS |
| `PREV`     | prev          , (*) |
| `WPREV`    | wprev         , (*)? |
| `IFTHEN`   | ifthen        , => |
| `ANDTHEN`  | andthen       , &> |
| `THEN`     | then          , ~> |
| `AFTER`    | after         , ~*> |
| `COUNT`    | count         , @ |
| `COUNTPAST` | countpast    , @* |
| `RELOP`    | <             , <= , = , != , >= , > |
| `REQUIRED` | ?             , ! |


## Contributing

- Tracy Clark (348B)
- Klaus Havelund (348B)
- Vivek Reddy (348B)
