import dataclasses

from lark import Lark, Transformer, v_args, Tree, Token

from zigzag.smt.src.formula_ast import *
from zigzag.smt.src.operators import *

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
        return LTLImplies(left, right)

    def or_(self, left, right):
        return LTLOr(left, right)

    def and_(self, left, right):
        return LTLAnd(left, right)

    def predicate(self, id_, *constraints):
        return PredicateFormula(id_, constraints) # maybe one needs to make it a list?

    def always(self, formula):
        return LTLAlways(formula)

    def eventually(self, formula):
        return LTLEventually(formula)

    def freeze(self, id_, field, formula):
        return LTLFreeze(id_, field, formula)

    def until(self, left, right):
        return LTLUntil(left, right)

    def since(self, left, right):
        return LTLSince(left, right)

    def sofar(self, formula):
        return LTLSofar(formula)

    def once(self, formula):
        return LTLOnce(formula)

    def next(self, formula):
        return LTLNext(formula)

    def weak_next(self, formula):
        return LTLWeakNext(formula)

    def prev(self, formula):
        return LTLWeakPrevious(formula)

    def weak_prev(self, formula):
        return LTLWeakPrevious(formula)

    def not_(self, formula):
        return LTLNot(formula)

    def parens(self, formula):
        return LTLParen(formula)

    def true(self):
        return LTLTrue()

    def false(self):
        return LTLFalse()

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

    formula_ = "! EXECUTE() & CLOSE() | OPEN() -> STOP(x=someField) & true"
    formula = "always DISPATCH() -> [d := degree] eventually EXECUTE(id = i)"
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
