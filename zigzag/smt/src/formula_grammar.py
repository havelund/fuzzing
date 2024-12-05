import dataclasses

from lark import Lark, Transformer, v_args, Tree, Token
from pprint import pprint

from zigzag.smt.src.formula_ast import *

grammar = """
?start: formula

?formula: formula "->" formula                      -> implies
        | formula "|" formula                       -> or_
        | formula "&" formula                       -> and_
        | ID "(" [constraint ("," constraint)*] ")" -> predicate
        | "always" formula                          -> always
        | "eventually" formula                      -> eventually
        | "[" ID ":=" ID "]" formula                -> freeze
        | formula "until" formula                   -> until
        | formula "since" formula                   -> since
        | "sofar" formula                           -> sofar
        | "once" formula                            -> once
        | "next" formula                            -> next
        | "wnext" formula                           -> weak_next
        | "prev" formula                            -> prev
        | "wprev" formula                           -> weak_prev
        | "!" formula                               -> not_
        | "(" formula ")"                           -> parens
        | "true"                                    -> true
        | "false"                                   -> false

constraint: ID "=" (ID | NUMBER)

%import common.CNAME -> ID
%import common.NUMBER
%import common.WS
%ignore WS
"""


@v_args(inline=True)
class FormulaTransformer(Transformer):
    def implies(self, left, right):
        return BinaryFormula(BinaryOp.IMPLIES, left, right)

    def or_(self, left, right):
        return BinaryFormula(BinaryOp.OR, left, right)

    def and_(self, left, right):
        return BinaryFormula(BinaryOp.AND, left, right)

    def predicate(self, id_, *constraints):
        return PredicateFormula(id_, constraints) # maybe one needs to make it a list?

    def always(self, formula):
        return UnaryFormula(UnaryOp.ALWAYS, formula)

    def eventually(self, formula):
        return UnaryFormula(UnaryOp.EVENTUALLY, formula)

    def freeze(self, id_, value, formula):
        return FreezeFormula(id_, value, formula)

    def until(self, left, right):
        return BinaryFormula(BinaryOp.UNTIL, left, right)

    def since(self, left, right):
        return BinaryFormula(BinaryOp.SINCE, left, right)

    def sofar(self, formula):
        return UnaryFormula(UnaryOp.SOFAR, formula)

    def once(self, formula):
        return UnaryFormula(UnaryOp.ONCE, formula)

    def next(self, formula):
        return UnaryFormula(UnaryOp.NEXT, formula)

    def weak_next(self, formula):
        return UnaryFormula(UnaryOp.WNEXT, formula)

    def prev(self, formula):
        return UnaryFormula(UnaryOp.PREV, formula)

    def weak_prev(self, formula):
        return UnaryFormula(UnaryOp.WPREV, formula)

    def not_(self, formula):
        return UnaryFormula(UnaryOp.NOT, formula)

    def parens(self, formula):
        return ParenFormula(formula)

    def true(self):
        return TrueFormula()

    def false(self):
        return FalseFormula()

    def ID(self, token):
        return str(token)























    def constraint(self, id_, value):
        return ArgumentConstraint(id_, value)


def pretty_print(tree, level=0):
    """Pretty prints a Lark parse tree."""
    indent = "  " * level
    if isinstance(tree, Tree):
        print(f"{indent}{tree.data}")
        for child in tree.children:
            pretty_print(child, level + 1)
    elif isinstance(tree, Token):
        print(f"{indent}{tree}")


if __name__ == "__main__":
    parser = Lark(grammar, parser="earley")

    formula = "! EXECUTE() & CLOSE() | OPEN() -> STOP(x=someField) & true"
    formula_ = "always DISPATCH() -> [i := identifier] eventually EXECUTE(id = i)"
    formula_ = "true"

    try:
        tree = parser.parse(formula)
        print("--- Formula: ---")
        print(formula)
        print("--- Tree: ---")
        print(tree)
        print("--- Tree pretty printed: ---")
        pretty_print(tree)
        print("--- AST: ---")
        ast = FormulaTransformer().transform(tree)
        ast.pretty_print()
    except Exception as e:
        print("Parsing error:", e)
