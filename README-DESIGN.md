
# Design Discussion

## Concepts

The following type definitions define some important concepts:

```python
CommandName = str
Argument = str
Command = tuple[CommandName, list[Argument]]
Test = list[Command]
TestSuite = list[Test]
CommandConstraint = Callable[[Command], bool]
TestConstraint = Callable[[Test], bool]
```

## Constraints

A test constraint is defined as a predicate _p_ on tests. 
Either a test _t_ satisfies it or not. That is, the test _t_ satisfies
_p_ iff:

```python
p(t) == True
```

Costraints can be applied at different times during the 
test generation, as described in the following, yielding 
increasingly more efficient solutions.

### After Generation of a Test

In this approch the test generating function repeatedly (until enough 
tests have been generated) generates a test _t_ and then applies
the predicate _p_ to the test, and if it returns True (and the test
has not been generated before) the test is included in the test suite.

This approach is simple but is the most costly since many futile
tests may be generated.

### After Generation of a Command

Here we try to verify command by command, and drop a command
(and re-generate a command) if the command together with the 
test generated so far does not satisfy some constraint.

It is better, but still not optimal efficiency wise.

And example is the following testing that max one `C1` command
is generated, where `cmd` is the next command generated:

```python
def maxOneC1(test: Test, cmd: Command) -> bool:
  return not cmd['command'] == 'C1' or not any(c in test if c['command'] == C1)
```

### Before Generating a Test/Command

In this solution we cut down on the dictionaries based on the constraints 
only allow randomization over allowed options. This can possibly be
done dynamically as we generate the test, command by command.
