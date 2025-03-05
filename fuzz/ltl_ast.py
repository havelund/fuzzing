
"""
This module defines the abstract syntax for the constraint language.
This includes also type checking (wellformedness check).
"""

from __future__ import annotations
from abc import ABC
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass, is_dataclass, fields
from collections import Counter

from fuzz.utils import CommandDict, Test, TestSuite
from fuzz.commands import *

Environment = Dict[str, Any]  # Environment maps strings to Z3 expressions (or ints)

TAB = '  '


# ==================================================================
# Auxiliary functions and data structures for static analysis
# ==================================================================

def report(msg: str):
    """Reports an error message.

    :param msg: the message to be printed.
    """
    print(f'*** ill formed: {msg}')


class SymbolTable:
    """The symbol table defining what commands exits, their argument types,
    as well as the variables in scope when a formula is checked for wellformedness.

    Attributes:
        cmd_env: a dictionary of dictionaries reflecting command and their argument types.
        var_env: variable types updated when variables are bound in a `LTLCommandMatch`.
    """
    def __init__(self):
        self.cmd_env: CommandTypeEnvironment = command_dictionary.generate_command_type_env()
        self.var_env: VariableTypeEnvironment = {}

    def copy(self) -> SymbolTable:
        """Makes a copy of the symbol table, keeping the `cmd_env` the same."""
        new_instance = SymbolTable.__new__(SymbolTable)  # Create uninitialized instance
        new_instance.cmd_env = self.cmd_env  # Keep reference to the same cmd_env
        new_instance.var_env = copy.deepcopy(self.var_env)
        return new_instance

    def is_command(self, cmd: str) -> bool:
        """A name is a command if it is defined as such or if it is `any`.

        :param cmd: the command name to check.
        :return: True if it is a defined command or `any`.
        """
        return cmd in self.cmd_env or cmd == 'any'

    def is_field(self, cmd: str, field: str) -> bool:
        """A name is a field of a command if defined as such.
        In the case the command name is `any`, it has to be a field of all commands,
        and their types should all be the same.

        :param cmd: the command name.
        :param field: the field of the command being checked.
        :return: True iff the field is a field of the command.
        """
        if not self.is_command(cmd):
            return False
        if cmd == 'any':
            defined_in_all = all(field in self.cmd_env[c] for c in self.cmd_env)
            if not defined_in_all:
                return False
            else:
                types = set([self.cmd_env[c][field] for c in self.cmd_env])
                return len(types) == 1
        else:
            var_env: VariableTypeEnvironment = self.cmd_env[cmd]
            return field in var_env

    def get_field_type(self, cmd: str, field: str) -> FieldType:
        """Returns the type if an argument field of a command.

        :param cmd: the command name.
        :param field: the field name.
        :return: the type of the field.
        """
        assert self.is_command(cmd)
        if cmd == 'any':
            var_envs = list(self.cmd_env.values())
            var_env = var_envs[0] # pick any, why not the first
            return var_env[field]
        else:
            assert field in self.cmd_env[cmd]
            return self.cmd_env[cmd][field]

    def update_variable_type(self, variable: str, ty: FieldType):
        """Updates a variable to have a type.

        :param variable: the variable name.
        :param ty: the type.
        """
        self.var_env[variable] = ty

    def is_variable(self, variable: str) -> bool:
        """Returns true of a variable is in scope.

        :param variable: the variable name.
        :return: True iff it is in scope.
        """
        return variable in self.var_env

    def get_variable_type(self, variable: str) -> FieldType:
        """Returns the type of a variable.

        :param variable: the variable name.
        :return: the type of the variable.
        """
        assert self.is_variable(variable)
        return self.var_env[variable]


# ==================================================================
# Other Auxiliary Functions
# ==================================================================

def unary_to_str(indent: int, oper: str, formula: LTLFormula) -> str:
    """Function used for pretty printing a unary formula, such as e.g. `next f`

    :param indent: the amount of indentations.
    :param oper: the unary operator.
    :param formula: the formula.
    :return: the formatted string.
    """
    result = TAB * indent
    result += oper + '\n'
    result += formula.to_str(indent + 1)
    return result


def binary_to_str(indent: int, left: LTLFormula, oper: str, right: LTLFormula) -> str:
    """Function used for pretty printing a binary formula, such as e.g. `f and g`

    :param indent: the amount of indentation.
    :param left: the leftmost formula.
    :param oper: the binary operator.
    :param right: the rightmost formula.
    :return: the formatted string.
    """
    result = ''
    result += f'{left.to_str(indent)}\n'
    result += TAB * indent + oper + '\n'
    result += f'{right.to_str(indent)}'
    return result


def within(index: int, test: Test) -> bool:
    """Checks whether an index is withing a test.

    :param index: the index.
    :param test: the test.
    :return: true iff the index is within the bounds of the test.
    """
    return 0 <= index < len(test)


def extract_field(command_name, field_name, command):
    """
    Extracts the value of a specified field from a Z3 Datatype instance,
    dynamically handling cases where the constructor is known or unknown.

    If the constructor is unknown (indicated by `command_name == "any"`), the function
    dynamically checks all constructors of the datatype to identify the field selector
    corresponding to the given field name. If the constructor is known, it directly
    uses the appropriate field selector.

    :param command_name: A string representing the name of the constructor, or "any"
                         if the constructor is unknown.
    :param field_name: A string representing the name of the field to extract (e.g., "time").
    :param command: A Z3 Datatype instance whose field value is to be extracted.

    :return: A Z3 expression representing the value of the specified field.

    :raises ValueError: If the specified field does not exist in any constructor
                        (when `command_name == "any"`) or if the command name is invalid.
    """
    if command_name == "any":
        # Dynamic check for field selector when constructor is unknown
        conditions = []
        fields = []

        # Add conditions for each constructor
        for i in range(Command.num_constructors()):
            constructor = Command.constructor(i)
            is_constructor = getattr(Command, f'is_{constructor.name()}')
            field_selector = getattr(Command, f'{constructor.name()}_{field_name}', None)
            if field_selector is not None:
                conditions.append(is_constructor(command))
                fields.append(field_selector(command))

        if not fields:
            raise ValueError(f"Field '{field_name}' does not exist in any constructor.")

        # Combine into a single If-Then-Else chain
        field_expr = fields[0]
        for condition, field_value in zip(conditions[1:], fields[1:]):
            field_expr = If(condition, field_value, field_expr)

        return field_expr
    else:
        # Directly use the field selector for the specified constructor
        selector = f'{command_name}_{field_name}'
        try:
            return getattr(Command, selector)(command)
        except AttributeError:
            raise ValueError(f"Field '{field_name}' does not exist in constructor '{command_name}'.")


# ==================================================================
# Abstract Syntax
# ==================================================================

@dataclass
class ASTNode(ABC):
    """
    Abstract class for all AST nodes, which must extend this.
    """

    # Color codes

    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

    def red(self, text: str) -> str:
        return f"{ASTNode.RED}{text}{ASTNode.RESET}"

    def blue(self, text: str) -> str:
        return f"{ASTNode.BLUE}{text}{ASTNode.RESET}"

    def green(self, text: str) -> str:
        return f"{ASTNode.GREEN}{text}{ASTNode.RESET}"

    def pretty_print(self, indent: int = 0):
        """Generic method to pretty print the dataclass instance with tree-like indentation.

        :param indent: the amount to indent.
        """
        TAB = 2
        indent_str = "|  " * indent
        cls_name = self.red(self.__class__.__name__)
        if is_dataclass(self) and fields(self):
            print(f"{indent_str}{cls_name}:")
        else:
            print(f"{indent_str}{cls_name}")
        if is_dataclass(self):
            for field in fields(self):
                value = getattr(self, field.name)
                field_name = self.blue(field.name)
                if isinstance(value, list):
                    print(f"{indent_str}|  {field_name}: [")
                    for item in value:
                        if isinstance(item, ASTNode):  # Nested ASTNode
                            item.pretty_print(indent + TAB + TAB)
                        else:
                            print(f"{indent_str}|    {self.green(item)}")  # Regular items
                    print(f"{indent_str}|  ]")
                elif isinstance(value, ASTNode):  # Nested ASTNode
                    print(f"{indent_str}|  {field_name}:")
                    value.pretty_print(indent + TAB)
                else:  # Other fields
                    print(f"{indent_str}|  {self.blue(field_name)}: {self.green(value)}")


@dataclass
class LTLExpression(ASTNode, ABC):
    """x or 10"""

    def to_str(self):
        """Returns a pretty printed version of the expression.
        :return: the pretty printed expression.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def to_smt(self, env: Environment) -> ExprRef:
        """Returns a Z3 representation of the expression.

        :param env: the environment defining variables in scope.
        :return: the Z3 representation of the expression.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def evaluate(self, env: Environment) -> object:
        """Evaluates the expression.

        :param env: the environment defining variables in scope.
        :return: the value of the expression.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def get_type(self, symbols: SymbolTable) -> FieldType:
        """Returns the type of an expression.

        :param symbols: the symbols table.
        :return: the type of the expression.
        """
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLBinaryExpression(LTLExpression):
    left: LTLExpression
    right: LTLExpression

    def get_type(self, symbols: SymbolTable) -> FieldType:
        left_type = self.left.get_type(symbols)
        right_type = self.right.get_type(symbols)
        if left_type == BaseType.FLOAT or right_type == BaseType.FLOAT:
            return BaseType.FLOAT
        elif left_type == BaseType.INT and right_type == BaseType.INT:
            return BaseType.INT
        else:
            raise TypeError("Operator requires numeric operands")

@dataclass
class LTLAddExpression(LTLBinaryExpression):
    def to_str(self) -> str:
        return f"({self.left.to_str()} + {self.right.to_str()})"

    def to_smt(self, env: Environment) -> ExprRef:
        return self.left.to_smt(env) + self.right.to_smt(env)

    def evaluate(self, env: Environment) -> Union[int, float]:
        return self.left.evaluate(env) + self.right.evaluate(env)


@dataclass
class LTLSubExpression(LTLBinaryExpression):
    def to_str(self) -> str:
        return f"({self.left.to_str()} - {self.right.to_str()})"

    def to_smt(self, env: Environment) -> ExprRef:
        return self.left.to_smt(env) - self.right.to_smt(env)

    def evaluate(self, env: Environment) -> Union[int, float]:
        return self.left.evaluate(env) - self.right.evaluate(env)


@dataclass
class LTLMulExpression(LTLBinaryExpression):
    def to_str(self) -> str:
        return f"({self.left.to_str()} * {self.right.to_str()})"

    def to_smt(self, env: Environment) -> ExprRef:
        return self.left.to_smt(env) * self.right.to_smt(env)

    def evaluate(self, env: Environment) -> Union[int, float]:
        return self.left.evaluate(env) * self.right.evaluate(env)


@dataclass
class LTLDivExpression(LTLBinaryExpression):
    def to_str(self) -> str:
        return f"({self.left.to_str()} / {self.right.to_str()})"

    def to_smt(self, env: Environment) -> ExprRef:
        return self.left.to_smt(env) / self.right.to_smt(env)

    def evaluate(self, env: Environment) -> Union[int, float]:
        return self.left.evaluate(env) / self.right.evaluate(env)


@dataclass
class LTLIDExpression(LTLExpression):
    """x"""

    ident: str

    def to_str(self):
        return self.ident

    def to_smt(self, env: Environment) -> ExprRef:
        return env[self.ident]

    def evaluate(self, env: Environment) -> object:
        return env[self.ident]

    def get_type(self, symbols: SymbolTable) -> FieldType:
        return symbols.get_variable_type(self.ident)


@dataclass
class LTLIntExpression(LTLExpression):
    """10"""

    number: int

    def to_str(self):
        return self.number.__str__()

    def to_smt(self, env: Environment) -> ExprRef:
        return IntVal(self.number)

    def evaluate(self, env: Environment) -> int:
        return self.number

    def get_type(self, symbols: SymbolTable) -> FieldType:
        return BaseType.INT


@dataclass
class LTLFloatExpression(LTLExpression):
    """10.5"""

    number: float

    def to_str(self):
        return self.number.__str__()

    def to_smt(self, env: Environment) -> ExprRef:
        return RealVal(self.number)

    def evaluate(self, env: Environment) -> int:
        return self.number

    def get_type(self, symbols: SymbolTable) -> FieldType:
        return BaseType.FLOAT


@dataclass
class LTLStringExpression(LTLExpression):
    """ "hello" """

    string: str

    def to_str(self):
        return f'"{self.string}"'

    def to_smt(self, env: Environment) -> ExprRef:
        return StringVal(self.string)

    def evaluate(self, env: Environment) -> str:
        return self.string

    def get_type(self, symbols: SymbolTable) -> FieldType:
        return BaseType.STRING


@dataclass
class LTLParenExpression(LTLExpression):
    """ (x+3)*y"""

    expr: LTLExpression

    def to_str(self):
        return f'({self.expr.to_str()})'

    def to_smt(self, env: Environment) -> ExprRef:
        return self.expr.to_smt(env)

    def evaluate(self, env: Environment) -> str:
        return self.expr.evaluate(env)

    def get_type(self, symbols: SymbolTable) -> FieldType:
        return self.expr.get_type(symbols)


@dataclass
class LTLConstraint(ASTNode,ABC):
    """Base class for all command parameter constraints."""

    def to_str(self):
        """Returns a pretty printed version of the constraint.
        :return: the pretty printed constraint.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        """Returns a Z3 representation of the constraint.

        :param env: the environment defining variables in scope.
        :param t: the current time.
        :param end_time: the end time of the timeline.
        :return: the Z3 representation of the constraint.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        """Evaluates the constraint.

        :param env: the environment defining variables in scope.
        :param cmd: dictionary mapping field names to their values.
        :return: the value of the expression.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def wellformed(self, symbols: SymbolTable) -> bool:
        """Checks if the constraint is wellformed. Reports if not.

        :param symbols: the symbol table.
        :return: True iff there are no errors.
        """
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLVariableConstraint(LTLConstraint):
    """cmd(id=x)"""

    command_name: str
    field: str  # id
    variable: str  # x

    def to_str(self):
        return f'{self.field} = {self.variable}'

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        actual_value = extract_field(self.command_name, self.field, timeline(t))
        return actual_value == env[self.variable]

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return cmd[self.field] == env[self.variable]

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok_field = symbols.is_field(self.command_name, self.field)
        if not ok_field:
            report(f'{self.field} is not a field of command {self.command_name}')
        ok_variable = symbols.is_variable(self.variable)
        if not ok_variable:
            report(f'{self.variable} is not in scope')
        if ok_field and ok_variable:
            ty1 = symbols.get_field_type(self.command_name, self.field)
            ty2 = symbols.get_variable_type(self.variable)
            number_types = [BaseType.INT, BaseType.FLOAT]
            ok_types = ty1 == ty2 or (ty1 in number_types and ty2 in number_types)
            if not ok_types:
                report(f'types of {self.field}:{ty1} and {self.variable}:{ty2} are not compatible')
        else:
            ok_types = False
        return ok_field and ok_variable and ok_types


@dataclass
class LTLVariableBinding(LTLConstraint):
    """cmd(id=x?)"""

    command_name: str
    field: str  # id
    variable: str  # x

    def to_str(self):
        return f'{self.field} = {self.variable}?'

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return True

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return True

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok_field = symbols.is_field(self.command_name, self.field)
        if not ok_field:
            report(f'{self.field} is not a field of command {self.command_name}')
        ok_variable = not symbols.is_variable(self.variable)
        if not ok_variable:
            report(f'{self.variable} is already in scope')
        if ok_field and ok_variable:
            ty = symbols.get_field_type(self.command_name, self.field)
            symbols.update_variable_type(self.variable, ty)
        return ok_field and ok_variable


@dataclass
class LTLNumberConstraint(LTLConstraint):
    """cmd(id=42)"""

    command_name: str
    field: str
    value: int

    def to_str(self):
        return f'{self.field} = {self.value}'

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        actual_value = extract_field(self.command_name, self.field, timeline(t))
        return actual_value == self.value

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return cmd[self.field] == self.value

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok_field = symbols.is_field(self.command_name, self.field)
        if not ok_field:
            report(f'{self.field} is not a field of command {self.command_name}')
        if ok_field:
            ty = symbols.get_field_type(self.command_name, self.field)
            ok_type = (ty == BaseType.INT or ty == BaseType.FLOAT)
            if not ok_type:
                report(f'type of {self.field}:{ty} is not Int or Float')
        else:
            ok_type = False
        return ok_field and ok_type


@dataclass
class LTLFloatConstraint(LTLConstraint):
    """cmd(id=42.5)"""

    command_name: str
    field: str
    value: float

    def to_str(self):
        return f'{self.field} = {self.value}'

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        actual_value = extract_field(self.command_name, self.field, timeline(t))
        return actual_value == self.value

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return cmd[self.field] == self.value

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok_field = symbols.is_field(self.command_name, self.field)
        if not ok_field:
            report(f'{self.field} is not a field of command {self.command_name}')
        if ok_field:
            ty = symbols.get_field_type(self.command_name, self.field)
            ok_type = (ty == BaseType.FLOAT)
            if not ok_type:
                report(f'type of {self.field}:{ty} is not Float')
        else:
            ok_type = False
        return ok_field and ok_type


@dataclass
class LTLStringConstraint(LTLConstraint):
    """cmd(id="abc")"""

    command_name: str
    field: str
    value: str

    def to_str(self):
        return f'{self.field} = "{self.value}"'

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        actual_value = extract_field(self.command_name, self.field, timeline(t))
        return actual_value == self.value

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return cmd[self.field] == self.value

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok_field = symbols.is_field(self.command_name, self.field)
        if not ok_field:
            report(f'{self.field} is not a field of command {self.command_name}')
        else:
            ty = symbols.get_field_type(self.command_name, self.field)
            if ty == BaseType.STRING:
                ok_type = True
            elif isinstance(ty, EnumType):
                if self.value not in ty.values:
                    report(f'{self.value} is not a member of enumerated type {ty.name}')
                    ok_type = False
                else:
                    ok_type = True
            else:
                report(f'{self.field}:{ty} does not have string type')
                ok_type = False
        return ok_field and ok_type


@dataclass
class LTLFormula(ASTNode,ABC):
    """Base class for all formulas."""

    def to_str(self, indent: int = 0):
        """Returns a pretty printed version of the constraint.

        :param indent: amount to indent.
        :return: the pretty printed formula.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        """Returns a Z3 representation of the formula.

        :param env: the environment defining variables in scope.
        :param t: the current time.
        :param end_time: the end time of the timeline.
        :return: the Z3 representation of the formula.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        """Evaluates the formula.

        :param env: the environment defining variables in scope.
        :param test: the test to evaluate the formula on.
        :param index: the current position in the test.
        :return: True iff the test satisfies the formula.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def wellformed(self, symbols: SymbolTable) -> bool:
        """Checks if the formula is wellformed. Reports if not.

        :param symbols: the symbol table.
        :return: True iff there are no errors.
        """
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLTrue(LTLFormula):
    """Represents a constraint that is True."""

    def to_str(self, indent: int = 0):
        return TAB * indent + 'true'

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return BoolVal(True)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return True

    def wellformed(self, symbols: SymbolTable) -> bool:
        return True



LTLTRUE = LTLTrue()  # Turn it into a singleton


@dataclass
class LTLFalse(LTLFormula):
    """Represents a constraint that is False."""

    def to_str(self, indent: int = 0):
        return TAB * indent + 'false'

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return BoolVal(False)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        return True


LTLFALSE = LTLFalse()  # Turn it into a singleton


@dataclass
class LTLRelation(LTLFormula):
    """x < 10"""
    exp1: LTLExpression
    oper: str
    exp2: LTLExpression

    def to_str(self, indent: int = 0):
        result = TAB * indent
        result += f'{self.exp1.to_str()} {self.oper} {self.exp2.to_str()}'
        return result

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        value1 = self.exp1.to_smt(env)
        value2 = self.exp2.to_smt(env)

        if self.oper == "<":
            return value1 < value2
        elif self.oper == "<=":
            return value1 <= value2
        elif self.oper == "=":
            return value1 == value2
        elif self.oper == "!=":
            return value1 != value2
        elif self.oper == ">":
            return value1 > value2
        elif self.oper == ">=":
            return value1 >= value2
        else:
            raise ValueError(f"Invalid relational operator: {self.oper}")

    def evaluate(self, env: Environment, t: int, end_time: int) -> bool:
        value1 = self.exp1.evaluate(env)
        value2 = self.exp2.evaluate(env)
        if self.oper == "<":
            return value1 < value2
        elif self.oper == "<=":
            return value1 <= value2
        elif self.oper == "=":
            return value1 == value2
        elif self.oper == "!=":
            return value1 != value2
        elif self.oper == ">":
            return value1 > value2
        elif self.oper == ">=":
            return value1 >= value2
        else:
            raise ValueError(f"Invalid relational operator: {self.oper}")

    def _enum_string(self, ty1: FieldType, ty2: FieldType, exp2: LTLExpression):
         if isinstance(ty1, EnumType) and ty2 == BaseType.STRING and isinstance(exp2, LTLStringExpression):
             return exp2.string in ty1.values
         else:
             return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        ty1 = self.exp1.get_type(symbols)
        ty2 = self.exp2.get_type(symbols)
        arithmetic_operators = ["<", "<=", ">", ">="]
        number_types = [BaseType.INT, BaseType.FLOAT]
        same_types = (
            ty1 == ty2 or
            (ty1 in number_types and ty2 in number_types) or
            self._enum_string(ty1, ty2, self.exp2) or
            self._enum_string(ty2, ty1, self.exp1)
        )
        if not same_types:
            report(f'expressions {self.exp1.to_str()} of type {ty1} and {self.exp2.to_str()} of type{ty2} do not have compatible types')
        comparable_types = (
                self.oper not in arithmetic_operators or
                (ty1 in number_types and ty2 in number_types)
        )
        if not comparable_types:
            report(f'expressions {self.exp1.to_str()} of type {ty1} and {self.exp2.to_str()} of type{ty2} do not match the operator {self.oper}')
        ok_types = same_types and comparable_types
        return ok_types


@dataclass
class LTLCommandMatch(LTLFormula):
    """cmd ?|! (field1=42,field2=x,field3=y?) => formula"""

    command_name: str
    constraints: list[LTLConstraint]
    arrow: str
    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        result = TAB * indent
        result += f'{self.command_name}('
        result += ','.join(c.to_str() for c in self.constraints)
        result += ')'
        result += f' {self.arrow}\n'
        result += self.subformula.to_str(indent + 1)
        return result

    def required(self) -> bool:
        return str(self.arrow) in ["&>", "andthen"]

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if self.command_name == 'any':
            right_command: BoolRef = True
        else:
            is_method: str = f'is_{self.command_name}'
            try:
                right_command: BoolRef = getattr(Command, is_method)(timeline(t))
            except AttributeError:
                raise ValueError(f"Invalid command name: {self.command_name}")
        right_arguments: list[BoolRef] = [constraint.to_smt(env, t, end_time) for constraint in self.constraints]
        event_constraint = And([right_command] + right_arguments)
        env_plus = env.copy()
        bindings = [c for c in self.constraints if isinstance(c, LTLVariableBinding)]
        for binding in bindings:
            env_plus[binding.variable] = extract_field(binding.command_name, binding.field, timeline(t))
        subformula_constraint = self.subformula.to_smt(env_plus, t, end_time)
        if self.required():
            final_constraint = And(event_constraint, subformula_constraint)
        else:
            final_constraint = Or(Not(event_constraint), subformula_constraint)
        return final_constraint

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            cmd = test[index]
            if cmd['name'] == self.command_name or self.command_name == 'any':
                constraints_satisfied = all([constraint.evaluate(env, cmd) for constraint in self.constraints])
                if constraints_satisfied:
                    env_plus = env.copy()
                    bindings = [c for c in self.constraints if isinstance(c, LTLVariableBinding)]
                    for binding in bindings:
                        field = binding.field
                        variable = binding.variable
                        env_plus[variable] = test[index][field]
                    return self.subformula.evaluate(env_plus, test, index)
        return not self.required()

    def wellformed(self, symbols: SymbolTable) -> bool:
        new_symbols = symbols.copy()
        ok_name = new_symbols.is_command(self.command_name)
        if not ok_name:
            report(f'command name {self.command_name} not valid')
        ok_constraints = True
        for constraint in self.constraints:
            ok_constraints &= constraint.wellformed(new_symbols)
        ok_formula = self.subformula.wellformed(new_symbols)
        return ok_name and ok_constraints and ok_formula


@dataclass
class LTLNot(LTLFormula):
    """LogicNot(φ): Logical negation !φ."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, '!', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Not(self.subformula.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return not self.subformula.evaluate(env, test, index)

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLAnd(LTLFormula):
    """LogicAnd(φ, ψ): Logical conjunction (φ ∧ ψ)."""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'and', self.right)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And(self.left.to_smt(env, t, end_time), self.right.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.left.evaluate(env, test, index) and self.right.evaluate(env, test, index)

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok1 = self.left.wellformed(symbols)
        ok2 = self.right.wellformed(symbols)
        return ok1 and ok2


@dataclass
class LTLOr(LTLFormula):
    """LogicOr(φ, ψ): Logical disjunction (φ ∨ ψ)."""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'or', self.right)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or(self.left.to_smt(env, t, end_time), self.right.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.left.evaluate(env, test, index) or self.right.evaluate(env, test, index)

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok1 = self.left.wellformed(symbols)
        ok2 = self.right.wellformed(symbols)
        return ok1 and ok2


@dataclass
class LTLImplies(LTLFormula):
    """LogicImplies(φ → ψ): Logical implication (φ → ψ)."""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, '->', self.right)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Implies(self.left.to_smt(env, t, end_time), self.right.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return not self.left.evaluate(env, test, index) or self.right.evaluate(env, test, index)

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok1 = self.left.wellformed(symbols)
        ok2 = self.right.wellformed(symbols)
        return ok1 and ok2


@dataclass
class LTLEventually(LTLFormula):
    """Eventually φ: at some point in the future, φ holds."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'eventually', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(t, end_time)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.subformula.evaluate(env, test, index) or self.evaluate(env, test, index + 1)
        return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLAlways(LTLFormula):
    """Always φ: at every point in the future, φ holds."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'always', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(t, end_time)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.subformula.evaluate(env, test, index) and self.evaluate(env, test, index + 1)
        return True

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)

@dataclass
class LTLNext(LTLFormula):
    """Next φ: in the next time step, φ holds."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'next', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.to_smt(env, t + 1, end_time)
        return BoolVal(False)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index + 1, test):
            return self.subformula.evaluate(env, test, index + 1)
        return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)

@dataclass
class LTLWeakNext(LTLFormula):
    """Weak Next φ: either φ holds in the next time step or the timeline ends."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'wnext', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.to_smt(env, t + 1, end_time)
        return BoolVal(True)  # If no next step, it's trivially true.

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index + 1, test):
            return self.subformula.evaluate(env, test, index + 1)
        return True

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLUntil(LTLFormula):
    """φ U ψ: φ holds until ψ holds at some point."""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'until', self.right)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([And(self.right.to_smt(env, t_prime, end_time),
                       And([self.left.to_smt(env, t_i, end_time) for t_i in range(t, t_prime)]))
                   for t_prime in range(t, end_time)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.right.evaluate(env, test, index) or (
                self.left.evaluate(env, test, index) and self.evaluate(env, test, index + 1)
            )
        return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok1 = self.left.wellformed(symbols)
        ok2 = self.right.wellformed(symbols)
        return ok1 and ok2


@dataclass
class LTLOnce(LTLFormula):
    """Once φ: at some point in the past, φ held."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'once', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(0, t + 1)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.subformula.evaluate(env, test, index) or self.evaluate(env, test, index - 1)
        return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLSofar(LTLFormula):
    """Historically φ: φ has always held in the past."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'sofar', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(0, t + 1)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.subformula.evaluate(env, test, index) and self.evaluate(env, test, index - 1)
        return True

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLPrevious(LTLFormula):
    """Previous φ: φ holds at the previous time step."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'prev', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.to_smt(env, t - 1, end_time)
        return BoolVal(False)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index - 1, test):
            return self.subformula.evaluate(env, test, index - 1)
        return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLWeakPrevious(LTLFormula):
    """Weak Previous φ: either φ holds at the previous time step or it's the start of the timeline."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        return unary_to_str(indent, 'wprev', self.subformula)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.to_smt(env, t - 1, end_time)
        return BoolVal(True)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index - 1, test):
            return self.subformula.evaluate(env, test, index - 1)
        return True

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLSince(LTLFormula):
    """φ S ψ: ψ holds at some point in the past, and φ has held since that point."""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'since', self.right)

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([And(self.right.to_smt(env, t_prime, end_time),
                       And([self.left.to_smt(env, t_i, end_time) for t_i in range(t_prime + 1, t + 1)]))
                   for t_prime in range(0, t + 1)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.right.evaluate(env, test, index) or (
                self.left.evaluate(env, test, index) and self.evaluate(env, test, index - 1)
            )
        return False

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok1 = self.left.wellformed(symbols)
        ok2 = self.right.wellformed(symbols)
        return ok1 and ok2


@dataclass
class LTLParen(LTLFormula):
    """(φ): holds if φ holds."""

    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        result = ''
        result += TAB * indent + '(\n'
        result += self.subformula.to_str(indent + 1)
        result += '\n'
        result += TAB * indent + ')'
        return result

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return self.subformula.to_smt(env, t, end_time)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.subformula.evaluate(env, test, index)

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.subformula.wellformed(symbols)


@dataclass
class LTLCountFuture(LTLFormula):
    """countfuture (5,10) φ."""

    min: int
    max: int
    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        oper = f'count({self.min},{self.max})'
        return unary_to_str(indent, oper, self.subformula)

    def count(self, env: Environment, test: Test, index: int) -> int:
        if within(index, test):
            number = 1 if self.subformula.evaluate(env, test, index) else 0
            return number + self.count(env, test, index + 1)
        return 0

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        counts = [
            If(self.subformula.to_smt(env, t_prime, end_time), IntVal(1), IntVal(0))
            for t_prime in range(t, end_time)
        ]
        total_count = Sum(counts)
        return And(self.min <= total_count, total_count <= self.max)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        number = self.count(env, test, index)
        return self.min <= number <= self.max

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok_min = self.min >= 0
        ok_max = self.min <= self.max
        ok_formula = self.subformula.wellformed(symbols)
        if not ok_min:
            report(f'{self.min} is negative')
        if not ok_max:
            report(f'{self.min} is bigger than {self.max}')
        return ok_min and ok_max and ok_formula


@dataclass
class LTLCountPast(LTLFormula):
    """countpast (5,10) φ."""

    min: int
    max: int
    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        oper = f'countpast({self.min},{self.max})'
        return unary_to_str(indent, oper, self.subformula)

    def count(self, env: Environment, test: Test, index: int) -> int:
        if within(index, test):
            number = 1 if self.subformula.evaluate(env, test, index) else 0
            return number + self.count(env, test, index - 1)
        return 0

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        counts = [
            If(self.subformula.to_smt(env, t_prime, end_time), IntVal(1), IntVal(0))
            for t_prime in range(0, t + 1)
        ]
        total_count = Sum(counts)
        return And(total_count >= self.min, total_count <= self.max)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        number = self.count(env, test, index)
        return self.min <= number <= self.max

    def wellformed(self, symbols: SymbolTable) -> bool:
        ok_min = self.min >= 0
        ok_max = self.min <= self.max
        ok_formula = self.subformula.wellformed(symbols)
        if not ok_min:
            report(f'{self.min} is negative')
        if not ok_max:
            report(f'{self.min} is bigger than {self.max}')
        return ok_min and ok_max and ok_formula


# ===================
# Derived Constructs:
# ===================

@dataclass
class LTLDerivedFormula(LTLFormula):
    """
    Abstract class for all derived formula. These are given semantics
    by expanding them to a formula in the core set of formulas.
    """
    def expand(self) -> LTLFormula:
        """Expland a formula to a formula representing its meaning."""
        raise NotImplementedError("Subclasses should implement this!")

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return self.expand().to_smt(env, t, end_time)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.expand().evaluate(env, test, index)

    def wellformed(self, symbols: SymbolTable) -> bool:
        return self.expand().wellformed(symbols)


@dataclass
class LTLPredicate(LTLDerivedFormula):
    """A generic constraint that evaluates an arbitrary expression on the environment and time point."""

    command_name: str
    constraints: list[LTLConstraint]

    def to_str(self, indent: int = 0):
        result = ''
        result += TAB * indent + self.command_name + '('
        result += ','.join(c.to_str() for c in self.constraints)
        result += ')'
        return result

    def expand(self) -> LTLFormula:
        return LTLCommandMatch(self.command_name, self.constraints, "andthen", LTLTrue())


@dataclass
class LTLThen(LTLDerivedFormula):
    """Represents the response constraint: tc1 ~> tc2 == [](tc1 -> <>tc2)"""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'then', self.right)

    def expand(self) -> LTLFormula:
        return LTLAlways(LTLImplies(self.left, LTLEventually(self.right)))


@dataclass
class LTLAfter(LTLDerivedFormula):
    """Represents the response constraint: tc1 ~*> tc2 == [](tc1 -> <*>tc2)"""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'after', self.right)

    def expand(self) -> LTLFormula:
        return LTLAlways(LTLImplies(self.left, LTLOnce(self.right)))


@dataclass
class LTLWeakUntil(LTLDerivedFormula):
    """Represents φ WU ψ as an abbreviation: (φ U ψ) ∨ []φ"""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'wuntil', self.right)

    def expand(self) -> LTLFormula:
        return LTLOr(LTLUntil(self.left, self.right), LTLAlways(self.left))


@dataclass
class LTLWeakSince(LTLDerivedFormula):
    """Represents φ WS ψ as an abbreviation: (φ S ψ) ∨ [*]φ"""

    left: LTLFormula
    right: LTLFormula

    def to_str(self, indent: int = 0):
        return binary_to_str(indent, self.left, 'wsince', self.right)

    def expand(self) -> LTLFormula:
        return LTLOr(LTLSince(self.left, self.right), LTLSofar(self.left))


@dataclass
class LTLCountFutureExact(LTLDerivedFormula):
    """countfuture 5 φ."""

    number: int
    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        oper = f'count {self.number}'
        return unary_to_str(indent, oper, self.subformula)

    def expand(self) -> LTLFormula:
        return LTLCountFuture(self.number, self.number, self.subformula)


@dataclass
class LTLCountPastExact(LTLDerivedFormula):
    """countpast 5 φ."""

    number: int
    subformula: LTLFormula

    def to_str(self, indent: int = 0):
        oper = f'countpast {self.number}'
        return unary_to_str(indent, oper, self.subformula)

    def expand(self) -> LTLFormula:
        return LTLCountPast(self.number, self.number, self.subformula)


@dataclass
class LTLMultiRelation(LTLDerivedFormula):
    """10 < x < 20"""
    exp1: LTLExpression
    oper1: str
    exp2: LTLExpression
    oper2: str
    exp3: LTLExpression

    def to_str(self, indent: int = 0):
        exp1_str = self.exp1.to_str()
        exp2_str = self.exp2.to_str()
        exp3_str = self.exp3.to_str()
        result = TAB * indent
        result += f'{exp1_str} {self.oper1} {exp2_str} {self.oper2} {exp3_str}'
        return result

    def expand(self) -> LTLFormula:
        return LTLAnd(
            LTLRelation(self.exp1, self.oper1, self.exp2),
            LTLRelation(self.exp2, self.oper2, self.exp3)
        )


@dataclass
class LTLRule(ASTNode):
    """(no)rule id: φ"""

    kw: str  # 'rule' or 'norule'
    rule_name: str
    formula: LTLFormula

    def to_str(self):
        result = ''
        result += f'{self.kw} {self.rule_name}:\n'
        result += f'{self.formula.to_str(1)}'
        return result

    def active(self) -> bool:
        return self.kw == 'rule'

    def to_smt(self, end_time: int) -> BoolRef:
        if self.active():
            return self.formula.to_smt({}, 0, end_time)
        else:
            return True

    def evaluate(self, test: Test) -> bool:
        if self.active():
            return self.formula.evaluate({}, test, 0)
        else:
            return True

    def wellformed(self) -> bool:
        if self.kw == 'norule':
            return True # we do not check the formula
        else:
            if not self.formula.wellformed(SymbolTable()):
                print('-------------------')
                print(self.formula.to_str())
                print('-------------------')
                return False
            else:
                return True


@dataclass
class LTLSpec(ASTNode):
    """collection of rules."""

    rules: list[LTLRule]

    def to_str(self):
        result = ''
        for rule in self.rules:
            result += f'{rule.to_str()}\n\n'
        return result

    def to_smt(self, end_time: int) -> BoolRef:
        smt_formulas: list[BoolRef] = [rule.to_smt(end_time) for rule in self.rules]
        return And(smt_formulas)

    def evaluate(self, test: Test) -> bool:
        return all(rule.evaluate(test) for rule in self.rules)

    def wellformed(self) -> bool:
        names = [rule.rule_name for rule in self.rules]
        counts = Counter(names)
        duplicates = {name for name, count in counts.items() if count > 1}
        ok_names = len(duplicates) == 0
        if not ok_names:
            report(f'duplicate rule names: {duplicates}')
        ok_rules = all([rule.wellformed() for rule in self.rules])
        return ok_names and ok_rules









