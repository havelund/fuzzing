
from abc import ABC
from typing import Dict, Any
from dataclasses import dataclass, is_dataclass, fields

from src.fuzz.utils import Test, CommandDict
from src.fuzz.commands import *

Environment = Dict[str, Any]  # Environment maps strings to Z3 expressions (or ints)


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


@dataclass
class ASTNode(ABC):
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

    def pretty_print(self, indent: int = 0) -> None:
        """Generic method to pretty print the dataclass instance with tree-like indentation."""
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
class LTLConstraint(ASTNode,ABC):
    """Base class for all command parameter constraints."""

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        raise NotImplementedError("Subclasses should implement this!")

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLVariableConstraint(LTLConstraint):
    """cmd(id=x)"""

    command_name: str
    field: str  # id
    variable: str  # x

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        actual_value = extract_field(self.command_name, self.field, timeline(t))
        return actual_value == env[self.variable]

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return cmd[self.field] == env[self.variable]

@dataclass
class LTLVariableBinding(LTLConstraint):
    """cmd(id=x?)"""

    command_name: str
    field: str  # id
    variable: str  # x

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return True

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return True


@dataclass
class LTLNumberConstraint(LTLConstraint):
    """cmd(id=42)"""

    command_name: str
    field: str
    value: int

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        actual_value = extract_field(self.command_name, self.field, timeline(t))
        return actual_value == self.value

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return cmd[self.field] == self.value


@dataclass
class LTLStringConstraint(LTLConstraint):
    """cmd(id="abc")"""

    command_name: str
    field: str
    value: str

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        actual_value = extract_field(self.command_name, self.field, timeline(t))
        return actual_value == self.value

    def evaluate(self, env: Environment, cmd: CommandDict) -> bool:
        return cmd[self.field] == self.value


@dataclass
class LTLFormula(ASTNode,ABC):
    """Base class for all formulas."""

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        raise NotImplementedError("Subclasses should implement this!")

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLTrue(LTLFormula):
    """Represents a constraint that is True."""

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return BoolVal(True)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return True


LTLTRUE = LTLTrue()  # Turn it into a singleton


@dataclass
class LTLFalse(LTLFormula):
    """Represents a constraint that is False."""

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return BoolVal(False)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return False


LTLFALSE = LTLFalse()  # Turn it into a singleton


@dataclass
class LTLCommandMatch(LTLFormula):
    """cmd ?|! (field1=42,field2=x,field3=y?) => formula"""

    command_name: str
    constraints: list[LTLConstraint]
    arrow: str
    subformula: LTLFormula

    def required(self) -> bool:
        return self.arrow in ["&>", "andthen"]

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if self.command_name == 'any':
            right_command: BoolRef = True
        else:
            is_method: str = f'is_{self.command_name}'
            right_command: BoolRef = getattr(Command, is_method)(timeline(t))
        right_arguments: list[BoolRef] = [constraint.to_smt(env, t, end_time) for constraint in self.constraints]
        event_constraint = And([right_command] + right_arguments)
        env_plus = env.copy()
        bindings = [c for c in self.constraints if isinstance(c, LTLVariableBinding)]
        binding_constraints = []
        for binding in bindings:
            frozen_value = Int(f'frozen_{binding.variable}_{t}')
            env_plus[binding.variable] = frozen_value
            actual_value = extract_field(binding.command_name, binding.field, timeline(t))
            freeze_constraint = frozen_value == actual_value
            binding_constraints.append(freeze_constraint)
        subformula_constraint = And(binding_constraints + [self.subformula.to_smt(env_plus, t, end_time)])
        if self.required():
            return And(event_constraint, subformula_constraint)
        else:
            return Or(Not(event_constraint), subformula_constraint)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            cmd = test[index]
            if cmd['name'] == self.command_name:
                constraints_satisfied = all(constraint.evaluate(env, cmd) for constraint in self.constraints)
                if constraints_satisfied:
                    env_plus = env.copy()
                    bindings = [c for c in self.constraints if isinstance(c, LTLVariableBinding)]
                    for binding in bindings:
                        field = binding.field
                        variable = binding.variable
                        debug(f'===> {test[index][field]}:{type(test[index][field])}')
                        env_plus[variable] = test[index][field]
                    return self.subformula.evaluate(env_plus, test, index)
        return not self.required()


@dataclass
class LTLNot(LTLFormula):
    """LogicNot(φ): Logical negation !φ."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Not(self.subformula.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return not self.subformula.evaluate(env, test, index)


@dataclass
class LTLAnd(LTLFormula):
    """LogicAnd(φ, ψ): Logical conjunction (φ ∧ ψ)."""

    left: LTLFormula
    right: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And(self.left.to_smt(env, t, end_time), self.right.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.left.evaluate(env, test, index) and self.right.evaluate(env, test, index)


@dataclass
class LTLOr(LTLFormula):
    """LogicOr(φ, ψ): Logical disjunction (φ ∨ ψ)."""

    left: LTLFormula
    right: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or(self.left.to_smt(env, t, end_time), self.right.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.left.evaluate(env, test, index) or self.right.evaluate(env, test, index)


@dataclass
class LTLImplies(LTLFormula):
    """LogicImplies(φ → ψ): Logical implication (φ → ψ)."""

    left: LTLFormula
    right: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Implies(self.left.to_smt(env, t, end_time), self.right.to_smt(env, t, end_time))

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return not self.left.evaluate(env, test, index) or self.right.evaluate(env, test, index)


@dataclass
class LTLEventually(LTLFormula):
    """Eventually φ: at some point in the future, φ holds."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(t, end_time)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.subformula.evaluate(env, test, index) or self.evaluate(env, test, index + 1)
        return False


@dataclass
class LTLAlways(LTLFormula):
    """Always φ: at every point in the future, φ holds."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(t, end_time)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            # ---\
            f1 = self.subformula.evaluate(env, test, index)
            f2 = self.evaluate(env, test, index + 1)
            debug(f'f1-formula={self.subformula}')
            debug(f'f1={f1}:{type(f1)}, f2={f2}:{type(f2)}')
            return f1 and f2
            # ---/
            return self.subformula.evaluate(env, test, index) and self.evaluate(env, test, index + 1)
        return True


@dataclass
class LTLNext(LTLFormula):
    """Next φ: in the next time step, φ holds."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.to_smt(env, t + 1, end_time)
        return BoolVal(False)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index + 1, test):
            return self.subformula.evaluate(env, test, index + 1)
        return False


@dataclass
class LTLWeakNext(LTLFormula):
    """Weak Next φ: either φ holds in the next time step or the timeline ends."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t + 1 < end_time:
            return self.subformula.to_smt(env, t + 1, end_time)
        return BoolVal(True)  # If no next step, it's trivially true.

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index + 1, test):
            return self.subformula.evaluate(env, test, index + 1)
        return True


@dataclass
class LTLUntil(LTLFormula):
    """φ U ψ: φ holds until ψ holds at some point."""

    left: LTLFormula
    right: LTLFormula

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


@dataclass
class LTLOnce(LTLFormula):
    """Once φ: at some point in the past, φ held."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return Or([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(0, t + 1)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.subformula.evaluate(env, test, index) or self.evaluate(env, test, index - 1)
        return False


@dataclass
class LTLSofar(LTLFormula):
    """Historically φ: φ has always held in the past."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return And([self.subformula.to_smt(env, t_prime, end_time) for t_prime in range(0, t + 1)])

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index, test):
            return self.subformula.evaluate(env, test, index) and self.evaluate(env, test, index - 1)
        return True


@dataclass
class LTLPrevious(LTLFormula):
    """Previous φ: φ holds at the previous time step."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.to_smt(env, t - 1, end_time)
        return BoolVal(False)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index - 1, test):
            return self.subformula.evaluate(env, test, index - 1)
        return False


@dataclass
class LTLWeakPrevious(LTLFormula):
    """Weak Previous φ: either φ holds at the previous time step or it's the start of the timeline."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        if t - 1 >= 0:
            return self.subformula.to_smt(env, t - 1, end_time)
        return BoolVal(True)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        if within(index - 1, test):
            return self.subformula.evaluate(env, test, index - 1)
        return True


@dataclass
class LTLSince(LTLFormula):
    """φ S ψ: ψ holds at some point in the past, and φ has held since that point."""

    left: LTLFormula
    right: LTLFormula

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


@dataclass
class LTLParen(LTLFormula):
    """(φ): holds if φ holds."""

    subformula: LTLFormula

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return self.subformula.to_smt(env, t, end_time)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.subformula.evaluate(env, test, index)


@dataclass
class LTLRule(ASTNode):
    """(no)rule id: φ"""

    kw: str  # 'rule' or 'norule'
    rule_name: str
    formula: LTLFormula

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


@dataclass
class LTLSpec(ASTNode):
    """collection of rules."""

    rules: list[LTLRule]

    def to_smt(self, end_time: int) -> BoolRef:
        smt_formulas: list[BoolRef] = [rule.to_smt(end_time) for rule in self.rules]
        return And(smt_formulas)

    def evaluate(self, test: Test) -> bool:
        return all(rule.evaluate(test) for rule in self.rules)

#######################
# Derived Constructs: #
#######################

@dataclass
class LTLDerivedFormula(LTLFormula):
    def expand(self) -> LTLFormula:
        raise NotImplementedError("Subclasses should implement this!")

    def to_smt(self, env: Environment, t: int, end_time: int) -> BoolRef:
        return self.expand().to_smt(env, t, end_time)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        return self.expand().evaluate(env, test, index)


@dataclass
class LTLPredicate(LTLDerivedFormula):
    """A generic constraint that evaluates an arbitrary expression on the environment and time point."""

    command_name: str
    constraints: list[LTLConstraint]

    def expand(self) -> LTLFormula:
        return LTLCommandMatch(self.command_name, self.constraints, "andthen", LTLTrue())


@dataclass
class LTLThen(LTLDerivedFormula):
    """Represents the response constraint: tc1 ~> tc2 == [](tc1 -> <>tc2)"""

    left: LTLFormula
    right: LTLFormula

    def expand(self) -> LTLFormula:
        return LTLAlways(LTLImplies(self.left, LTLEventually(self.right)))


@dataclass
class LTLAfter(LTLDerivedFormula):
    """Represents the response constraint: tc1 ~*> tc2 == [](tc1 -> <*>tc2)"""

    left: LTLFormula
    right: LTLFormula

    def expand(self) -> LTLFormula:
        return LTLAlways(LTLImplies(self.left, LTLOnce(self.right)))


@dataclass
class LTLWeakUntil(LTLDerivedFormula):
    """Represents φ WU ψ as an abbreviation: (φ U ψ) ∨ []φ"""

    left: LTLFormula
    right: LTLFormula

    def expand(self) -> LTLFormula:
        return LTLOr(LTLUntil(self.left, self.right), LTLAlways(self.left))


@dataclass
class LTLWeakSince(LTLDerivedFormula):
    """Represents φ WS ψ as an abbreviation: (φ S ψ) ∨ [*]φ"""

    left: LTLFormula
    right: LTLFormula

    def expand(self) -> LTLFormula:
        return LTLOr(LTLSince(self.left, self.right), LTLSofar(self.left))


###################
# New Constructs: #
###################

@dataclass
class LTLCountFuture(LTLFormula):
    """countfuture (5,10) φ."""

    min: int
    max: int
    subformula: LTLFormula

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
        return And(total_count >= self.min, total_count <= self.max)

    def evaluate(self, env: Environment, test: Test, index: int) -> bool:
        number = self.count(env, test, index)
        return self.min <= number <= self.max


@dataclass
class LTLCountPast(LTLFormula):
    """countpast (5,10) φ."""

    min: int
    max: int
    subformula: LTLFormula

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


@dataclass
class LTLExpression(ASTNode, ABC):
    """x or 10"""

    def to_smt(self, env: Environment) -> ExprRef:
        raise NotImplementedError("Subclasses should implement this!")

    def evaluate(self, env: Environment) -> object:
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class LTLIDExpression(LTLExpression):
    """x"""

    ident: str

    def to_smt(self, env: Environment) -> ExprRef:
        return env[self.ident]

    def evaluate(self, env: Environment) -> object:
        debug(f'##### env={env}, type({self.ident})={type(env[self.ident])}') # z3 type IntNumRef
        return env[self.ident]


@dataclass
class LTLNumberExpression(LTLExpression):
    """10"""

    number: int

    def to_smt(self, env: Environment) -> BoolRef:
        return IntVal(self.number)

    def evaluate(self, env: Environment) -> int:
        return self.number


@dataclass
class LTLRelation(LTLFormula):
    """x < 10"""
    exp1: LTLExpression
    oper: str
    exp2: LTLExpression

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
        debug(f'@@@@@@@@ env={env}, exp1={self.exp1}, exp2={self.exp2}')
        debug(f'@@@@@@@@ value1={value1}, value2={value2}')
        debug(f'@@@@@@@@ type1={type(value1)}, type2={type(value2)}')
        if self.oper == "<":
            debug(f'value1={value1} < value2={value2} == {value1 < value2}')
            return value1 < value2
        elif self.oper == "<=":
            return value1 <= value2
        elif self.oper == "=":
            debug(f'value1={value1} = value2={value2} == {value1 == value2}: {type(value1 == value2)}')
            return value1 == value2
        elif self.oper == "!=":
            return value1 != value2
        elif self.oper == ">":
            return value1 > value2
        elif self.oper == ">=":
            return value1 >= value2
        else:
            raise ValueError(f"Invalid relational operator: {self.oper}")


@dataclass
class LTLMultiRelation(LTLDerivedFormula):
    """10 < x < 20"""
    exp1: LTLExpression
    oper1: str
    exp2: LTLExpression
    oper2: str
    exp3: LTLExpression

    def expand(self) -> LTLFormula:
        return LTLAnd(
            LTLRelation(self.exp1, self.oper1, self.exp2),
            LTLRelation(self.exp2, self.oper2, self.exp3)
        )

