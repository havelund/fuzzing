
"""
This module defines the grammar and parser for the constraint language.
It uses the lark parser generator: https://github.com/lark-parser/lark.
"""

from lark import Lark, Transformer, v_args, Tree, Token
from graphviz import Digraph

from fuzz.options import Options
from fuzz.ltl_ast import *

# ============
# The grammar.
# ============

grammar = """
?start: specification

?specification: rule* -> spec

?rule: RULE ID ":" formula -> rule

?formula: formula IMPLIES formula           -> implies
        | ID "(" constraints? ")" (IFTHEN | ANDTHEN) formula -> commandmatch
        | "[" ID "(" constraints? ")" "]" formula -> commandmatch_ifthen
        | "<" ID "(" constraints? ")" ">" formula -> commandmatch_andthen
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
        | COUNT "(" INT "," INT ")" formula -> countfuture               // NOT LTL
        | COUNTPAST   "(" INT "," INT ")" formula -> countpast           // NOT LTL
        | COUNT INT  formula              -> countfutureexact            // DERIVED
        | COUNTPAST INT formula           -> countpastexact              // DERIVED
        | formula THEN formula               -> then                     // DERIVED
        | formula AFTER formula              -> after                    // DERIVED
        
?expression: sum

?sum: product
    | sum "+" product         -> addexpr
    | sum "-" product         -> subexpr

?product: primary
        | product "*" primary -> mulexpr
        | product "/" primary -> divexpr

?primary: ID                  -> idexpr
        | INT                 -> intexpr
        | FLOAT               -> floatexpr
        | STRING              -> stringexpr
        | "(" expression ")"  -> parenexpr

constraints: constraint ("," constraint)*   -> constraint_list

constraint: ID "=" ID                       -> varconstraint
          | ID "=" ID "?"                   -> varbinding 
          | ID "=" INT                      -> intconstraint
          | ID "=" FLOAT                    -> floatconstraint
          | ID "=" STRING                   -> stringconstraint

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
%import common.ESCAPED_STRING -> STRING
%import common.SIGNED_INT -> INT
%import common.SIGNED_FLOAT -> FLOAT

%import common.WS
%ignore WS
%ignore COMMENT
"""

# =====================================
# Converting the parse tree to our AST.
# =====================================

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

    def commandmatch_ifthen(self, id_, *args):
        if len(args) == 1:
            constraints = []
            formula = args[0]
        elif len(args) == 2:
            constraints = args[0]
            formula = args[1]
        else:
            raise ValueError("Unexpected number of arguments in commandmatch_ifthen")
        for constraint in constraints:
            constraint.command_name = id_
        return LTLCommandMatchIfThen(id_, constraints, formula)

    def commandmatch_andthen(self, id_, *args):
        if len(args) == 1:
            constraints = []
            formula = args[0]
        elif len(args) == 2:
            constraints = args[0]
            formula = args[1]
        else:
            raise ValueError("Unexpected number of arguments in commandmatch_andthen")
        for constraint in constraints:
            constraint.command_name = id_
        return LTLCommandMatchAndThen(id_, constraints, formula)

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

    def floatconstraint(self, id_, value):
        return LTLFloatConstraint('place_holder_for_command', id_, float(value))

    def stringconstraint(self, id_, value):
        unquoted_value = value[1:-1]
        return LTLStringConstraint('place_holder_for_command', id_, unquoted_value)

    # New constructs:

    def countfuture(self, kw, min, max, formula):
        return LTLCountFuture(int(min), int(max), formula)

    def countpast(self, kw, min, max, formula):
        return LTLCountPast(int(min), int(max), formula)

    def countfutureexact(self, kw, number, formula):
        return LTLCountFutureExact(int(number), formula)

    def countpastexact(self, kw, number, formula):
        return LTLCountPastExact(int(number), formula)

    def relation(self, exp1, kw, exp2):
        return LTLRelation(exp1, kw, exp2)

    def addexpr(self, expr1, expr2):
        return LTLAddExpression(expr1, expr2)

    def subexpr(self, expr1, expr2):
        return LTLSubExpression(expr1, expr2)

    def mulexpr(self, expr1, expr2):
        return LTLMulExpression(expr1, expr2)

    def divexpr(self, expr1, expr2):
        return LTLDivExpression(expr1, expr2)

    def idexpr(self, id):
        return LTLIDExpression(id)

    def intexpr(self, number):
        return LTLIntExpression(int(number))

    def floatexpr(self, number):
        return LTLFloatExpression(float(number))

    def stringexpr(self, string):
        unquoted_value = string[1:-1]
        return LTLStringExpression(unquoted_value)

    def parenexpr(self, expr):
        return LTLParenExpression(expr)

    # Derived constructs:

    def then(self, left, kw, right):
        return LTLThen(left, right)

    def after(self, left, kw, right):
        return LTLAfter(left, right)

    def multirelation(self, exp1, kw1, exp2, kw2, exp3):
        return LTLMultiRelation(exp1, kw1, exp2, kw2, exp3)

# ================================
# Methods for visualizing the AST.
# ================================

def pretty_print(tree, level=0):
    """Pretty prints a Lark parse tree."""
    indent = "  " * level
    if isinstance(tree, Tree):
        print(f"{indent}{tree.data}")
        for child in tree.children:
            pretty_print(child, level + 1)
    elif isinstance(tree, Token):
        print(f"{indent}{tree}")


def visualize_parse_tree(tree: Tree):
    graph = visualize_sub_tree(tree)
    graph.render("parse_tree", view=True)


def visualize_sub_tree(tree: Tree, graph=None, parent=None):
    if graph is None:
        graph = Digraph(format="png")
        graph.attr("node", shape="circle")
    node_id = str(id(tree))
    graph.node(node_id, tree.data if isinstance(tree, Tree) else str(tree))
    if parent is not None:
        graph.edge(parent, node_id)
    if isinstance(tree, Tree):
        for child in tree.children:
            visualize_sub_tree(child, graph, node_id)
    return graph

# =====================
# The parsing function.
# =====================

def parse_spec(spec: str) -> LTLSpec:
    """Parses the specification, generates an AST,
    which is checked for wellformedness, and returns the AST.
    If the AST is not wellformed the program stops.

    :param spec: the specification of constraints.
    :return: the AST representing the specification.
    """
    parser = Lark(grammar, parser="earley")
    try:
        tree = parser.parse(spec)
        if Options.GRAPH_PARSE_TREE:
            visualize_parse_tree(tree)
        ast: LTLSpec = FormulaTransformer().transform(tree)
        # headline('AST')
        # ast.pretty_print()
        headline('SPECIFICATION')
        print(ast.to_str())
        if not ast.wellformed():
            print("Specification is not wellformed")
            sys.exit(1)
        return ast
    except Exception as e:
        print("Parsing error:", e)
        sys.exit(1)


