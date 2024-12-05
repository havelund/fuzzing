from abc import ABC
from dataclasses import dataclass, is_dataclass, fields
from enum import Enum


class UnaryOp(Enum):
    NOT = "!"
    ALWAYS = "always"
    EVENTUALLY = "eventually"
    SOFAR = "sofar"
    ONCE = "once"
    NEXT = "next"
    WNEXT = "wnext"
    PREV = "prev"
    WPREV = "wprev"


class BinaryOp(Enum):
    IMPLIES = "->"
    OR = "|"
    AND = "&"
    UNTIL = "until"
    SINCE = "since"
    SOFAR = "sofar"
    ONCE = "once"


@dataclass
class ArgumentConstraint:
    argument: str
    value: str | int


@dataclass
class Formula(ABC):
    def pretty_print(self, indent: int = 0) -> None:
        """Generic method to pretty print the dataclass instance with tree-like indentation."""
        TAB = 2
        indent_str = "|  " * indent
        cls_name = self.__class__.__name__
        if is_dataclass(self) and fields(self):
            print(f"{indent_str}{cls_name}:")
        else:
            print(f"{indent_str}{cls_name}")
        if is_dataclass(self):
            for field in fields(self):
                value = getattr(self, field.name)
                if isinstance(value, Formula):
                    value.pretty_print(indent + TAB)
                else:
                    print(f"{indent_str}|  {field.name}: {value}")


@dataclass
class TrueFormula(Formula):
    pass


@dataclass
class FalseFormula(Formula):
    pass


@dataclass
class UnaryFormula(Formula):
    oper: UnaryOp
    formula: Formula


@dataclass
class BinaryFormula(Formula):
    oper: BinaryOp
    left: Formula
    right: Formula


@dataclass
class ParenFormula(Formula):
    formula: Formula


@dataclass
class FreezeFormula(Formula):
    variable: str
    argument: str
    formula: Formula


@dataclass
class PredicateFormula(Formula):
    name: str
    constraints: list[ArgumentConstraint]




