
from lark import Lark, Transformer, v_args, Tree, Token

from src.fuzz.ltl_ast import *

grammar = """
?start: specification

?specification: rule* -> spec

?rule: RULE ID ":" formula -> rule

?formula: formula IMPLIES formula           -> implies
        | ID "(" constraints? ")" (IFTHEN | ANDTHEN) formula -> commandmatch
        | formula OR formula                -> or_
        | formula AND formula               -> and_
        | ID "(" constraints? ")"           -> predicate
        | ALWAYS formula                    -> always
        | EVENTUALLY formula                -> eventually
        | formula UNTIL formula             -> until
        | formula WUNTIL formula            -> weakuntil                 // DERIVED
        | formula SINCE formula             -> since
        | formula WSINCE formula            -> weaksince                 // DERIVED
        | SOFAR formula                     -> sofar
        | ONCE formula                      -> once
        | NEXT formula                      -> next
        | WNEXT formula                     -> weak_next
        | PREV formula                      -> prev
        | WPREV formula                     -> weak_prev
        | NOT formula                       -> not_
        | expression RELOP expression       -> relation
        | expression RELOP expression RELOP expression  -> multirelation // DERIVED
        | "(" formula ")"                   -> parens
        | "true"                            -> true
        | "false"                           -> false
        | COUNT "(" NUMBER "," NUMBER ")" formula       -> countfuture   // NOT LTL
        | COUNTPAST   "(" NUMBER "," NUMBER ")" formula -> countpast     // NOT LTL
        | formula THEN formula               -> then                     // DERIVED
        | formula AFTER formula              -> after                    // DERIVED
        
?expression: ID                             -> idexpr
           | NUMBER                         -> numberexpr

constraints: constraint ("," constraint)*   -> constraint_list

constraint: ID "=" ID                       -> varconstraint
          | ID "=" ID "?"                   -> varbinding 
          | ID "=" NUMBER                   -> intconstraint

RULE: "rule" | "norule"

NOT: "not" | "!"
IMPLIES: "implies" | "->"
OR: "or" | "|"
AND: "and" | "&"

ALWAYS: "always" | "[]"
EVENTUALLY: "eventually" | "<>"
UNTIL: "until" | "U"
WUNTIL: "wuntil" | "WU"
NEXT: "next" | "()"
WNEXT: "wnext" | "()?"

SOFAR: "sofar" | "[*]"
ONCE: "once" | "<*>"
SINCE: "since" | "S"
WSINCE: "wsince" | "WS"
PREV: "prev" | "(*)"
WPREV: "wprev" | "(*)?"

IFTHEN: "ifthen" | "=>"
ANDTHEN: "andthen" | "&>"

THEN: "then" | "~>"
AFTER: "after" | "~*>"
COUNT: "count" | "@"
COUNTPAST: "countpast" | "@*"
RELOP: "<" | "<=" | "=" | "!=" | ">=" | ">"
REQUIRED: "?" | "!"

COMMENT: /\#[^\r\n]*/x 

%import common.CNAME -> ID
%import common.NUMBER
%import common.WS
%ignore WS
%ignore COMMENT
"""


@v_args(inline=True)
class FormulaTransformer(Transformer):
    def spec(self, *rules):
        return LTLSpec(list(rules))

    def rule(self, kw, name, formula):
        return LTLRule(kw, name, formula)

    def implies(self, left, kw, right):
        return LTLImplies(left, right)

    def commandmatch(self, id_, *args):
        if len(args) == 2:
            constraints = []
            kw = args[0]
            formula = args[1]
        elif len(args) == 3:
            constraints = args[0]
            kw = args[1]
            formula = args[2]
        else:
            raise ValueError("Unexpected number of arguments in commandmatch")
        for constraint in constraints:
            constraint.command_name = id_
        return LTLCommandMatch(id_, constraints, kw, formula)

    def or_(self, left, kw, right):
        return LTLOr(left, right)

    def and_(self, left, kw, right):
        return LTLAnd(left, right)

    def predicate(self, id_, constraints=None):
        constraints_list = constraints if constraints is not None else []
        for constraint in constraints_list:
            constraint.command_name = id_
        return LTLPredicate(id_, constraints_list)

    def always(self, kw, formula):
        return LTLAlways(formula)

    def eventually(self, kw, formula):
        return LTLEventually(formula)

    def until(self, left, kw, right):
        return LTLUntil(left, right)

    def weakuntil(self, left, kw, right):
        return LTLWeakUntil(left, right)

    def since(self, left, kw, right):
        return LTLSince(left, right)

    def weaksince(self, left, kw, right):
        return LTLWeakSince(left, right)

    def sofar(self, kw, formula):
        return LTLSofar(formula)

    def once(self, kw, formula):
        return LTLOnce(formula)

    def next(self, kw, formula):
        return LTLNext(formula)

    def weak_next(self, kw, formula):
        return LTLWeakNext(formula)

    def prev(self, kw, formula):
        return LTLWeakPrevious(formula)

    def weak_prev(self, kw, formula):
        return LTLWeakPrevious(formula)

    def not_(self, kw, formula):
        return LTLNot(formula)

    def parens(self, formula):
        return LTLParen(formula)

    def true(self):
        return LTLTrue()

    def false(self):
        return LTLFalse()

    def ID(self, token):
        return str(token)

    def constraint_list(self, *constraints):
        return list(constraints)

    def varconstraint(self, id_, value):
        return LTLVariableConstraint('place_holder_for_command', id_, value)

    def varbinding(self, id_, value):
        return LTLVariableBinding('place_holder_for_command', id_, value)

    def intconstraint(self, id_, value):
        return LTLNumberConstraint('place_holder_for_command', id_, int(value))

    # New constructs:

    def countfuture(self, kw, min, max, formula):
        return LTLCountFuture(int(min), int(max), formula)

    def countpast(self, kw, min, max, formula):
        return LTLCountPast(int(min), int(max), formula)

    def relation(self, exp1, kw, exp2):
        return LTLRelation(exp1, kw, exp2)

    def idexpr(self, id):
        return LTLIDExpression(id)

    def numberexpr(self, number):
        return LTLNumberExpression(int(number))

    # Derived constructs:

    def then(self, left, kw, right):
        return LTLThen(left, right)

    def after(self, left, kw, right):
        return LTLAfter(left, right)

    def multirelation(self, exp1, kw1, exp2, kw2, exp3):
        return LTLMultiRelation(exp1, kw1, exp2, kw2, exp3)


def pretty_print(tree, level=0):
    """Pretty prints a Lark parse tree."""
    indent = "  " * level
    if isinstance(tree, Tree):
        print(f"{indent}{tree.data}")
        for child in tree.children:
            pretty_print(child, level + 1)
    elif isinstance(tree, Token):
        print(f"{indent}{tree}")


def parse_spec(spec: str) -> LTLSpec:
    parser = Lark(grammar, parser="earley")
    try:
        tree = parser.parse(spec)
        print("--- Specification: ---")
        print(spec)
        print("--- Tree: ---")
        print(tree)
        print("--- Tree pretty printed: ---")
        pretty_print(tree)
        print("--- AST: ---")
        ast = FormulaTransformer().transform(tree)
        ast.pretty_print()
        return ast
    except Exception as e:
        print("Parsing error:", e)
        sys.exit(1)


if __name__ == "__main__":
    parser = Lark(grammar, parser="earley")

    spec = """
    rule p1 : ! EXECUTE() & CLOSE() | OPEN(y=3) -> STOP(x=someField, y=3) & true 
    rule p2 : always DISPATCH() -> [d := degree] eventually EXECUTE(id = i)
    rule p3 : true
    """

    ast = parse_spec(spec)
    print(ast)