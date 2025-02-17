# fuzz

**THIS PAGE IS UNDER (RE)CONSTRUCTION**

**Version**: 2.0.0

## Introduction

This repository contains a library `fuzz` for fuzz testing
flight software. The main function, `generate_tests`, provided by the library, generates a test suite,
which is a list of tests. Each test is a list of commands, which can be sent
to the flight software from a FIT script. Each test is randomly generated, optionally
restricted by user provided constraints.
The objective of fuzzing is to invoke unlikely, untried, command sequences on the flight
software in an attempt to break it.

The function `generate_tests` takes as input a description of possible commands in XML format,
a description of what particular flight software modules should be tested (areas),
and an optinal specification of constraints, which limits the amount of randomness,
allowing to avoid unrealistic command sequences or to focus on specific command sequences of interest. 
Tests are generated using a constraint solver ([z3](https://github.com/Z3Prover/z3)).

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

A complete demo example is shown in [src/tests/demo](https://github.jpl.nasa.gov/lars/fuzzing/tree/main/tests/demo2), which shall be
our throughgoing example.  

The folder contains a folder `fsw` with the definitions of commands, a configuration file `fuzz_config.json`,
a file `spec.txt` containing in this case one constraint, and finally the script `fit.py` which generates test cases.
Run the script to test the installation:

```
python fit.py
```

## The Command Dictionary

Test generation is based on a description of what commands, inclcuding types and ranges
of their arguments, which can be submitted to the SUO. This command dictionary is provided
as an XML file, as is commont for JPL flight missions.
In this section we shall describe how this looks like.

We based our description on an artificial example with commands for operating a rover.
Using an informal succinct notation (in contrast to XML which is quite verbose), we consider
the following eight commands.

```python
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

The command set offers commands for moving (`MOVE`) a rover, 
aligning (`ALIGN`) the rover to face in a particular absolute direction, 
turning (`TURN`) the rover a relative number of degrees,
cancel (`CANCEL`) a command,
stop (`STOP`) a driving,
take a picture (`PIC`),
send (`SEND`) pictures to ground,
log (`LOG`) data.

Each command carries a time stamp and a command number. Types are indicated as (unsigned) `uint`, `float`, 'string',
or the name of an enumerated type, in this case `speed` and `image_quality`: 

```python
types
    speed = {"slow", "medium", "fast"}
    image_quality = {"low", "high"}
```

For numeric types a range is indicated with lower and upper bound
between square brackets. For strings the length is indicated between square brackets.

These commands are now represented formally as collection of XML files, each of which 
has the following format, defining an entry of enumeration
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

The complete XML file for our example is shown [here](tests/demo2/fsw/src/mov_mgr/mov_mgr_ai_cmd.xml).
These files must be stored in a folder, here named `fsw` with the following structure:

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

## The Configuration File

The folder contains a configuration file named `fuzz_config.json` (it must have this name). In our case it looks as follows.

```json
{
    "fsw_path": "fsw",
    "fsw_areas": ["mov"],
    "spec_path": "spec.txt",
    "test_suite_size": 10,
    "test_size": 10
}
```

Explanation:

- **fsw_path**: the path to the folder containing the command definitions.
- **fsw_areas**: a list of the areas for which commands should be generated.
- **spec_path**: the path to the specification of constraints. Note that this is optional as the specification
  can be provided in the script, which it is in our case.
- **test_suite_size**: the number of tests to be generated.
- **test_size**: the number of commands in each test.

Instead of providing the configuration file as a member of the folder one can define its location
using the following environment variable: `FUZZ_CONFIG_PATH`.

## The Test Script

The folder contains the following script `fit.py`, which underneath reads the configuration file,
and then the XML command dictionary indicated in the configuration file.

```python
from src.fuzz import generate_tests, TestSuite

spec = """
    rule time_moves_forward:
      always any(time=t1?) => wnext any(time=t2?) => t1 < t2

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
    tests: TestSuite = generate_tests(spec=spec, test_suite_size=2, test_size=10)
    for test_nr, test in enumerate(tests):
        print(f'\n=== test nr. {test_nr} ===\n')
        for cmd in test:
            print(cmd)
```

### Imports

The script imports the `generate_tests` function from the fuzz library, and the type `TestSuite` which is the result
type of the function.

### The Specification of Constraints

It then defines a specification of constraints as a text string, here named
`spec`. If the `spec` was empty (`spec = ""`), `generate_tests` will generate completely random commands, although respecting the minimal
and maximal bounds provided in the XML command dictionary. We here briefly explain the constraints, a full explanation of the constraint language
is provided below. The specification consists of five constraints, all of which each generated  test (command sequence) must satisfy. The language in which these constraints
is a temporal logic. The five properties state:

- **time_moves_forward**: This property states that for any command with a time value `t1`, if there is a next command (we are not
  at the end of the command list = weak next) with a time value `t2`, then `t2` is strictly bigger than `t1`.

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

### The `generate_tests` Function

The script then calls the `generate_tests` function, which has the following type:

```python
def generate_tests(spec: Optional[str] = None, test_suite_size: Optional[int] = None, test_size: Optional[int] = None) -> TestSuite
```

It returns a test suite, which is a list of tests, each consisting of a list of commands. The `TestSuite` type is defined 
as follows.

```python
CommandDict = Dict[str, Union[int, float, str]]
Test = List[CommandDict]
TestSuite = List[Test]
```

The function reads definitions of commands and their argument types, including enumerations,
from the XML dictionary pointed out in the configuration file. It takes as argument the 
specification of constraints, how many tests to generate (`test_suite_size`) and how many commands in each 
test (`test_size`). Note that in case any of the three arguments is left out, the default values in the configuration file
are used.

At this point it is up to the script writer how to use the tests. We here go through each test in a `for` loop, 
and for each command in a test we print it out. For testing purposes, we would here submit the command to the SUT.

### Run the Script

Running the script

```
python fit.py
```

can yield the following output (note that there is dandomness in the output):

```
=== test nr. 0 ===

{'name': 'SEND', 'time': 360, 'number': 90, 'images': 25, 'message': 'PEgQXr670x'}
{'name': 'CANCEL', 'time': 755, 'number': 17, 'message': 'gL0DhifwUb'}
{'name': 'ALIGN', 'time': 757, 'number': 47, 'angle': -129.71814708552742, 'message': ''}
{'name': 'TURN', 'time': 759, 'number': 75, 'angle': -3.0, 'message': 'ooBo'}
{'name': 'TURN', 'time': 764, 'number': 26, 'angle': 7.0, 'message': ''}
{'name': 'STOP', 'time': 766, 'number': 38, 'message': 'xC0N5H0ukh'}
{'name': 'PIC', 'time': 995, 'number': 92, 'images': 2, 'quality': 'high', 'message': 'GiLfzecqRR'}
{'name': 'ALIGN', 'time': 996, 'number': 27, 'angle': -129.59314708552742, 'message': 'o'}
{'name': 'MOVE', 'time': 997, 'number': 93, 'distance': 95, 'speed': 3.0, 'message': ''}
{'name': 'STOP', 'time': 999, 'number': 93, 'message': 'oo'}

=== test nr. 1 ===

{'name': 'LOG', 'time': 285, 'number': 30, 'message': 'TywNkxqiZA'}
{'name': 'LOG', 'time': 952, 'number': 53, 'message': 'S0ebT2qCDA'}
{'name': 'ALIGN', 'time': 961, 'number': 51, 'angle': 48.93563793402194, 'message': ''}
{'name': 'ALIGN', 'time': 968, 'number': 85, 'angle': 49.06063793402194, 'message': 'h'}
{'name': 'MOVE', 'time': 972, 'number': 58, 'distance': 98, 'speed': 1.0, 'message': ''}
{'name': 'TURN', 'time': 977, 'number': 16, 'angle': 3.0, 'message': 'B'}
{'name': 'TURN', 'time': 979, 'number': 56, 'angle': 6.0, 'message': ''}
{'name': 'CANCEL', 'time': 983, 'number': 44, 'message': ''}
{'name': 'TURN', 'time': 984, 'number': 91, 'angle': -9.0, 'message': ''}
{'name': 'STOP', 'time': 1000, 'number': 58, 'message': 'B'}
```

The reader can try and convince him or herself, that each of these two tests satisfies the constraints.

## Constraint Language

We first provide a very quick introduction to the general principles of temporal logic, and then
subsequently present our temporal logic.

### General Introduction to Temporal Logic

We all know Boolean logic: `true`, `false`, `P and Q` (`P /\ Q`), 
`P or Q` (`P \/ Q`), and `P implies Q` (`P -> Q`). Boolean logic allows to formulate
statements about e.g. Python dictionaties. Say we want to describe the properties of the dictionary:

```python
d = {'x': 1, 'y': 2}
```

It satisfies e.g. the Boolean property:

```python
'x' in d and 'y' in d and d['x'] < d['y'] 
```

Note that there are in fact many dictionaries (in fact infinitelyt many) that satisfy this property, e.g. also:

```python
d = {'x': 10, 'y': 200, 'z': 2, 'p': 2}
```
Temporal logic allows us to formulate statements about a _sequence_ of things, for example, in our
case, a sequence of dictionaries. Take for example the following sequence of five dictionaries:

```python
s = [
  {'x': 0, 'y': 1}, 
  {'x': 2, 'y': 3}, 
  {'x': 4, 'y': 5}, 
  {'x': 6, 'y': 7}, 
  {'x': 8, 'y': 9}
]
```

The following temporal properties using the temporal operators **always**, **eventually**, 
and **next**, are all true about this sequence (we here just refer
to the variables, the meaning should be clear):

1. **always** x < y
2. **eventually** x == 6
3. **not eventually** x >= 9
4. **always** x < 9
5. **always** x == 2 implies **next** x == 4
5. **always** ((x < 8 **and** x _has a value_ k) **implies next** x == k+2)

For example a sequence satisfies `always F` if F is true in every 
single position of the sequence.  A sequence satisfies `eventually F` if `F`
is true at some position in the future. A sequence satisfies `next F` if `F`
is true at the next future position.

We can evaluate a sequence like the one above and check that it
satisfies the formulas. As you may have guessed, we can also turn this around
and from the formulas generate sequences that satisfy them. This is exactly our
test generation task.

### Introduction to the Temporal Logic MATL

The constraint language is a temporal logic with future and past time
operators, and which enables capturing values of command arguments in
one part of a formula, and refer to them  in another part of the formula.
As an example, consider the test (from our previous example):

```
[
  {'name': 'SEND', 'time': 360, 'number': 90, 'images': 25, 'message': 'PEgQXr670x'},
  {'name': 'CANCEL', 'time': 755, 'number': 17, 'message': 'gL0DhifwUb'},
  {'name': 'ALIGN', 'time': 757, 'number': 47, 'angle': -129.71814708552742, 'message': ''},
  {'name': 'TURN', 'time': 759, 'number': 75, 'angle': -3.0, 'message': 'ooBo'},
  {'name': 'TURN', 'time': 764, 'number': 26, 'angle': 7.0, 'message': ''},
  {'name': 'STOP', 'time': 766, 'number': 38, 'message': 'xC0N5H0ukh'},
  {'name': 'PIC', 'time': 995, 'number': 92, 'images': 2, 'quality': 'high', 'message': 'GiLfzecqRR'},
  {'name': 'ALIGN', 'time': 996, 'number': 27, 'angle': -129.59314708552742, 'message': 'o'},
  {'name': 'MOVE', 'time': 997, 'number': 93, 'distance': 95, 'speed': 3.0, 'message': ''},
  {'name': 'STOP', 'time': 999, 'number': 93, 'message': 'oo'}
] 
```

This test satisfies for example the following formula: 
  
    always MOVE(number=n?) => eventually STOP(number=n) 

We have here taken the liberty to refer to command names and arguments ina  special manner. 
The property states:

- It is **always** the case, for any position in the sequence, that if this is
  a `MOVE` command with a `number` argument which is _n_, then after that follows
  **eventually** a `STOP` command with the same `number` argument _n_.

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

A special command name is `any`. This will match any command.

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
