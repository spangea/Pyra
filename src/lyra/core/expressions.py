"""
Expressions
===========

Lyra's internal representation of Python expressions.

:Authors: Caterina Urban and Simon Wehrli
"""

from abc import ABCMeta, abstractmethod
from enum import IntEnum, Enum
from typing import Set, List

from apronpy.coeff import PyMPQScalarCoeff, PyMPQIntervalCoeff
from apronpy.interval import PyMPQInterval
from apronpy.lincons0 import ConsTyp
from apronpy.tcons1 import PyTcons1
from apronpy.texpr0 import TexprOp, TexprRtype, TexprRdir
from apronpy.texpr1 import PyTexpr1
from apronpy.var import PyVar

from lyra.core.types import LyraType, StringLyraType, IntegerLyraType, BooleanLyraType, \
    DictLyraType, SetLyraType, ListLyraType, TupleLyraType, SequenceLyraType, ContainerLyraType, TopLyraType
from lyra.core.utils import copy_docstring

class Status(Enum):
    YES = "YES"
    MAYBE = "MAYBE"
    NO = "NO"

class Expression(metaclass=ABCMeta):
    """Expression representation.

    https://docs.python.org/3.4/reference/expressions.html
    """

    def __init__(self, typ: LyraType):
        """Expression construction.

        :param typ: (result) type of the expression
        """
        self._typ = typ

    @property
    def typ(self):
        return self._typ

    @abstractmethod
    def __eq__(self, other: 'Expression'):
        """Expression equality.

        :param other: other expression to compare
        :return: whether the expression equality holds
        """

    @abstractmethod
    def __hash__(self):
        """Expression hash representation.

        :return: hash value representing the expression
        """

    def __ne__(self, other: 'Expression'):
        return not (self == other)

    @abstractmethod
    def __str__(self):
        """Expression string representation.

        :return: string representing the expression
        """

    def ids(self) -> Set['VariableIdentifier']:
        """Identifiers that appear in the expression.

        :return: set of identifiers that appear in the expression
        """
        ids = set()
        for expr in walk(self):
            if isinstance(expr, VariableIdentifier):
                ids.add(expr)
        return ids


def _iter_child_exprs(expr: Expression):
    """
    Yield all direct child expressions of ``expr``,
    that is, all fields that are expressions
    and all items of fields that are lists of expressions.
    """
    for _, field in expr.__dict__.items():
        if isinstance(field, Expression):
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, Expression):
                    yield item


def walk(expr: Expression):
    """
    Recursively yield all expressions in an expression tree
    starting at ``expr`` (including ``expr`` itself),
    in no specified order.
    """
    from collections import deque
    todo = deque([expr])
    while todo:
        expr = todo.popleft()
        todo.extend(_iter_child_exprs(expr))
        yield expr


# noinspection PyPep8Naming
class ExpressionVisitor(metaclass=ABCMeta):
    """
    An expression visitor base class that walks the expression tree and calls a
    visitor function for every expression found.  This function may return a value
    which is forwarded by the `visit` method.

    Subclasses are meant to implement the visitor functions.
    The visitor function for an expression is ``'visit_'`` +
    class name of the expression.  So a `Literal` expression visit function would
    be `visit_Literal`.  If no visitor function exists for an expression
    a `NotImplementedError` is raised.

    Adapted from `ast.py`.
    """

    def visit(self, expr, *args, **kwargs):
        """Visit of an expression."""
        method = 'visit_' + expr.__class__.__name__
        if hasattr(self, method):
            return getattr(self, method)(expr, *args, **kwargs)
        error = f"Missing visitor for {expr.__class__.__name__} in {self.__class__.__qualname__}!"
        raise NotImplementedError(error)

    @abstractmethod
    def visit_Literal(self, expr: 'Literal'):
        """Visit of a literal expression."""

    @abstractmethod
    def visit_VariableIdentifier(self, expr: 'VariableIdentifier'):
        """Visit of a variable identifier."""

    @abstractmethod
    def visit_LengthIdentifier(self, expr: 'LengthIdentifier'):
        """Visit of a sequence or collection length."""

    @abstractmethod
    def visit_ListDisplay(self, expr: 'ListDisplay'):
        """Visit of a list display."""

    @abstractmethod
    def visit_TupleDisplay(self, expr: 'TupleDisplay'):
        """Visit of a tuple display."""

    @abstractmethod
    def visit_SetDisplay(self, expr: 'SetDisplay'):
        """Visit of a set display."""

    @abstractmethod
    def visit_DictDisplay(self, expr: 'DictDisplay'):
        """Visit of dictionary display."""

    @abstractmethod
    def visit_AttributeReference(self, expr: 'AttributeReference'):
        """Visit of an attribute reference."""

    @abstractmethod
    def visit_Subscription(self, expr: 'Subscription'):
        """Visit of a subscription expression."""

    @abstractmethod
    def visit_Slicing(self, expr: 'Slicing'):
        """Visit of a slicing expression."""

    @abstractmethod
    def visit_Input(self, expr: 'Input'):
        """Visit of an input call expression."""

    @abstractmethod
    def visit_Range(self, expr: 'Range'):
        """Visit of a range call expression."""

    @abstractmethod
    def visit_Keys(self, expr: 'Keys'):
        """Visit of a keys call expression."""

    @abstractmethod
    def visit_Values(self, expr: 'Values'):
        """Visit of a values call expression."""

    @abstractmethod
    def visit_CastOperation(self, expr: 'CastOperation'):
        """Visit of a cast operation."""

    @abstractmethod
    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation'):
        """Visit of a unary arithmetic operation."""

    @abstractmethod
    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation'):
        """Visit of a unary boolean operation."""

    @abstractmethod
    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation'):
        """Visit of a binary arithmetic operation."""

    @abstractmethod
    def visit_BinarySequenceOperation(self, expr: 'BinarySequenceOperation'):
        """Visit of a binary sequence operation."""

    @abstractmethod
    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation'):
        """Visit of a binary boolean operation."""

    @abstractmethod
    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation'):
        """Visit of a binary comparison operation."""

    def generic_visit(self, expr, *args, **kwargs):
        raise ValueError(
            f"{self.__class__.__qualname__} does not support generic visit of expressions! "
            f"Define handling for a {expr.__class__.__name__} expression explicitly!")


class NegationFreeExpression(ExpressionVisitor):
    """Expression visitor that removes negations using De Morgan's law."""

    @copy_docstring(ExpressionVisitor.visit_Literal)
    def visit_Literal(self, expr: 'Literal', invert=False):
        if invert:
            if isinstance(expr.typ, BooleanLyraType):
                if expr.val == 'True':
                    return Literal(BooleanLyraType(), 'False')
                assert expr.val == 'False'
                return Literal(BooleanLyraType(), 'True')
            elif isinstance(expr.typ, IntegerLyraType):
                if float(expr.val) != 0:
                    return Literal(BooleanLyraType(), 'False')
                assert float(expr.val) == 0
                return Literal(BooleanLyraType(), 'True')
            assert isinstance(expr.typ, StringLyraType)
            if expr.val:
                return Literal(BooleanLyraType(), 'False')
            return Literal(BooleanLyraType(), 'True')
        return expr    # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
    def visit_VariableIdentifier(self, expr: 'VariableIdentifier', invert=False):
        if isinstance(expr.typ, BooleanLyraType) and invert:
            operator = UnaryBooleanOperation.Operator.Neg
            return UnaryBooleanOperation(BooleanLyraType(), operator, expr)
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
    def visit_LengthIdentifier(self, expr: 'LengthIdentifier', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_ListDisplay)
    def visit_ListDisplay(self, expr: 'ListDisplay', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
    def visit_TupleDisplay(self, expr: 'TupleDisplay', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_SetDisplay)
    def visit_SetDisplay(self, expr: 'SetDisplay', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_DictDisplay)
    def visit_DictDisplay(self, expr: 'DictDisplay', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_AttributeReference)
    def visit_AttributeReference(self, expr: 'AttributeReference', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Subscription)
    def visit_Subscription(self, expr: 'Subscription', invert=False):
        if isinstance(expr.typ, BooleanLyraType) and invert:
            operator = UnaryBooleanOperation.Operator.Neg
            return UnaryBooleanOperation(BooleanLyraType(), operator, expr)
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Slicing)
    def visit_Slicing(self, expr: 'Slicing', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Input)
    def visit_Input(self, expr: 'Input', invert=False):
        return expr

    @copy_docstring(ExpressionVisitor.visit_Range)
    def visit_Range(self, expr: 'Range', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Keys)
    def visit_Keys(self, expr: 'Keys', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Values)
    def visit_Values(self, expr: 'Values', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_CastOperation)
    def visit_CastOperation(self, expr: 'CastOperation'):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', invert=False):
        if expr.operator == UnaryBooleanOperation.Operator.Neg:
            return self.visit(expr.expression, invert=not invert)
        raise ValueError(f"Unary boolean operator {expr.operator} is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
    def visit_BinarySequenceOperation(self, expr: 'BinarySequenceOperation', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', invert=False):
        left = self.visit(expr.left, invert)
        operator = expr.operator.reverse_operator() if invert else expr.operator
        right = self.visit(expr.right, invert)
        return BinaryBooleanOperation(expr.typ, left, operator, right)

    @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', invert=False):
        left = expr.left
        operator = expr.operator.reverse_operator() if invert else expr.operator
        right = expr.right
        return BinaryComparisonOperation(expr.typ, left, operator, right, expr.forloop)


class NegationFreeNormalExpression(ExpressionVisitor):
    """
    An expression visitor that:

    1. removes negations using De Morgan's law, and

    2. puts all boolean comparison operations with ``=``, ``!=``, ``<``, ``<=``, ``>``, and ``>=``
       in the normal form ``expr <= 0``.
    """

    @copy_docstring(ExpressionVisitor.visit_Literal)
    def visit_Literal(self, expr: 'Literal', invert=False):
        return expr    # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
    def visit_VariableIdentifier(self, expr: 'VariableIdentifier', invert=False):
        if isinstance(expr.typ, BooleanLyraType) and invert:
            operator = UnaryBooleanOperation.Operator.Neg
            return UnaryBooleanOperation(BooleanLyraType(), operator, expr)
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
    def visit_LengthIdentifier(self, expr: 'LengthIdentifier', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_ListDisplay)
    def visit_ListDisplay(self, expr: 'ListDisplay', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
    def visit_TupleDisplay(self, expr: 'TupleDisplay', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_SetDisplay)
    def visit_SetDisplay(self, expr: 'SetDisplay', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_DictDisplay)
    def visit_DictDisplay(self, expr: 'DictDisplay', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_AttributeReference)
    def visit_AttributeReference(self, expr: 'AttributeReference', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Subscription)
    def visit_Subscription(self, expr: 'Subscription', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Slicing)
    def visit_Slicing(self, expr: 'Slicing', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Input)
    def visit_Input(self, expr: 'Input', invert=False):
        return expr

    @copy_docstring(ExpressionVisitor.visit_Range)
    def visit_Range(self, expr: 'Range', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Keys)
    def visit_Keys(self, expr: 'Keys', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Values)
    def visit_Values(self, expr: 'Keys', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_CastOperation)
    def visit_CastOperation(self, expr: 'CastOperation'):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', invert=False):
        if expr.operator == UnaryBooleanOperation.Operator.Neg:
            return self.visit(expr.expression, invert=not invert)
        raise ValueError(f"Unary boolean operator {expr.operator} is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
    def visit_BinarySequenceOperation(self, expr: 'BinarySequenceOperation', invert=False):
        return expr  # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', invert=False):
        left = self.visit(expr.left, invert)
        operator = expr.operator.reverse_operator() if invert else expr.operator
        right = self.visit(expr.right, invert)
        return BinaryBooleanOperation(expr.typ, left, operator, right)

    @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', invert=False):
        left = expr.left
        operator = expr.operator.reverse_operator() if invert else expr.operator
        right = expr.right
        if operator == BinaryComparisonOperation.Operator.Eq:
            # left = right -> left - right <= 0 && right - left <= 0
            zero = Literal(IntegerLyraType(), "0")
            minus = BinaryArithmeticOperation.Operator.Sub
            operator = BinaryComparisonOperation.Operator.LtE
            expr1 = BinaryArithmeticOperation(left.typ, left, minus, right)
            expr1 = BinaryComparisonOperation(expr.typ, expr1, operator, zero)
            expr2 = BinaryArithmeticOperation(right.typ, right, minus, left)
            expr2 = BinaryComparisonOperation(expr.typ, expr2, operator, zero)
            conjunction = BinaryBooleanOperation.Operator.And
            return BinaryBooleanOperation(expr.typ, expr1, conjunction, expr2)
        elif operator == BinaryComparisonOperation.Operator.NotEq:
            # left != right -> left - (right - 1) <= 0 || right - (left - 1) <= 0
            zero = Literal(IntegerLyraType(), "0")
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            operator = BinaryComparisonOperation.Operator.LtE
            expr1 = BinaryArithmeticOperation(right.typ, right, minus, one)
            expr1 = BinaryArithmeticOperation(left.typ, left, minus, expr1)
            expr1 = BinaryComparisonOperation(expr.typ, expr1, operator, zero)
            expr2 = BinaryArithmeticOperation(left.typ, left, minus, one)
            expr2 = BinaryArithmeticOperation(right.typ, right, minus, expr2)
            expr2 = BinaryComparisonOperation(expr.typ, expr2, operator, zero)
            disjunction = BinaryBooleanOperation.Operator.Or
            return BinaryBooleanOperation(expr.typ, expr1, disjunction, expr2)
        elif operator == BinaryComparisonOperation.Operator.Lt:
            # left < right -> left - (right - 1) <= 0
            zero = Literal(IntegerLyraType(), "0")
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            right = BinaryArithmeticOperation(right.typ, right, minus, one)
            left = BinaryArithmeticOperation(left.typ, left, minus, right)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, left, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.LtE:
            # left <= right -> left - right <= 0
            zero = Literal(IntegerLyraType(), "0")
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(left.typ, left, minus, right)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, left, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.Gt:
            # left > right -> right - (left - 1) <= 0
            zero = Literal(IntegerLyraType(), "0")
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(left.typ, left, minus, one)
            right = BinaryArithmeticOperation(right.typ, right, minus, left)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, right, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.GtE:
            # left >= right -> right - left <= 0
            zero = Literal(IntegerLyraType(), "0")
            minus = BinaryArithmeticOperation.Operator.Sub
            right = BinaryArithmeticOperation(right.typ, right, minus, left)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, right, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.In:
            return BinaryComparisonOperation(expr.typ, left, operator, right, expr.forloop)
        elif operator == BinaryComparisonOperation.Operator.NotIn:
            return BinaryComparisonOperation(expr.typ, left, operator, right, expr.forloop)
        raise ValueError(f"Boolean comparison operator {expr} is unsupported!")


class Lyra2APRON(ExpressionVisitor):
    """Expression visitor that yields APRON tree expressions and constraints."""

    @copy_docstring(ExpressionVisitor.visit_Literal)
    def visit_Literal(self, expr: 'Literal', environment=None, usub=False) -> PyTexpr1:
        if usub:
            cst = PyMPQScalarCoeff(-float(expr.val))
        else:
            cst = PyMPQScalarCoeff(float(expr.val))
        return PyTexpr1.cst(environment, cst)

    @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
    def visit_VariableIdentifier(self, expr, environment=None, usub=False) -> PyTexpr1:
        assert not usub
        return PyTexpr1.var(environment, PyVar(expr.name))

    @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
    def visit_LengthIdentifier(self, expr: 'LengthIdentifier', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_ListDisplay)
    def visit_ListDisplay(self, expr: 'ListDisplay', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
    def visit_TupleDisplay(self, expr: 'TupleDisplay', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_SetDisplay)
    def visit_SetDisplay(self, expr: 'SetDisplay', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_DictDisplay)
    def visit_DictDisplay(self, expr: 'DictDisplay', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_AttributeReference)
    def visit_AttributeReference(self, expr: 'AttributeReference', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_Subscription)
    def visit_Subscription(self, expr: 'Subscription', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_Slicing)
    def visit_Slicing(self, expr: 'Slicing', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_Input)
    def visit_Input(self, expr, environment=None, usub=False) -> PyTexpr1:
        assert not usub
        return PyTexpr1.cst(environment, PyMPQIntervalCoeff(PyMPQInterval.top()))

    @copy_docstring(ExpressionVisitor.visit_Range)
    def visit_Range(self, expr: 'Range', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_Keys)
    def visit_Keys(self, expr: 'Keys', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_Values)
    def visit_Values(self, expr: 'Keys', environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_CastOperation)
    def visit_CastOperation(self, expr: 'CastOperation'):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
    def visit_UnaryArithmeticOperation(self, expr, environment=None, usub=False) -> PyTexpr1:
        usub = expr.operator == UnaryArithmeticOperation.Operator.Sub
        return self.visit(expr.expression, environment, usub)

    @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
    def visit_UnaryBooleanOperation(self, expr, environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
    def visit_BinaryArithmeticOperation(self, expr, environment=None, usub=False) -> PyTexpr1:
        assert not usub
        expr1 = self.visit(expr.left, environment)
        expr2 = self.visit(expr.right, environment)
        op2op = {
            BinaryArithmeticOperation.Operator.Add: TexprOp.AP_TEXPR_ADD,
            BinaryArithmeticOperation.Operator.Sub: TexprOp.AP_TEXPR_SUB,
            BinaryArithmeticOperation.Operator.Mult: TexprOp.AP_TEXPR_MUL,
            BinaryArithmeticOperation.Operator.Div: TexprOp.AP_TEXPR_DIV
        }
        op = op2op[expr.operator]
        return PyTexpr1.binop(op, expr1, expr2, TexprRtype.AP_RTYPE_REAL, TexprRdir.AP_RDIR_RND)

    @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
    def visit_BinarySequenceOperation(self, expr, environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
    def visit_BinaryBooleanOperation(self, expr, environment=None, usub=False):
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
    def visit_BinaryComparisonOperation(self, expr, environment=None, usub=False) -> PyTcons1:
        assert not usub
        typ = expr.left.typ
        left = expr.left
        right = expr.right
        sub = BinaryArithmeticOperation.Operator.Sub
        if expr.operator == BinaryComparisonOperation.Operator.GtE:
            expr = self.visit(BinaryArithmeticOperation(typ, left, sub, right), environment)
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUPEQ)
        elif expr.operator == BinaryComparisonOperation.Operator.Gt:
            expr = self.visit(BinaryArithmeticOperation(typ, left, sub, right), environment)
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUP)
        elif expr.operator == BinaryComparisonOperation.Operator.LtE:
            expr = self.visit(BinaryArithmeticOperation(typ, right, sub, left), environment)
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUPEQ)
        elif expr.operator == BinaryComparisonOperation.Operator.Lt:
            expr = self.visit(BinaryArithmeticOperation(typ, right, sub, left), environment)
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUP)
        raise ValueError(f"Conversion of {expr} to APRON is unsupported!")


"""
Atomic Expressions
https://docs.python.org/3.4/reference/expressions.html#atoms
"""


class Literal(Expression):
    """Literal representation.

    https://docs.python.org/3.4/reference/expressions.html#literals
    """

    def __init__(self, typ: LyraType, val: str):
        """Literal construction.

        :param typ: type of the literal
        :param val: value of the literal
        """
        super().__init__(typ)
        self._val = val

    @property
    def val(self):
        return self._val

    def __eq__(self, other: 'Literal'):
        return (self.typ, self.val) == (other.typ, other.val)

    def __hash__(self):
        return hash((self.typ, self.val))

    def __str__(self):
        if isinstance(self.typ, StringLyraType):
            return f'"{self.val}"'
        return f"{self.val}"


class Identifier(Expression, metaclass=ABCMeta):
    """Identifier representation.

    https://docs.python.org/3.4/reference/expressions.html#atom-identifiers
    """

    def __init__(self, typ: LyraType, name: str, special: bool = False):
        """Identifier construction.

        :param typ: type of the identifier
        :param name: name of the identifier
        :param special: whether this is a special identifier
        """
        super().__init__(typ)
        self._name = name
        self._special = special

    @property
    def name(self):
        return self._name

    @property
    def special(self):
        return self._special

    def __eq__(self, other: 'Identifier'):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return "{0.name}".format(self)


class VariableIdentifier(Identifier):
    """Variable identifier representation."""

    def __init__(self, typ: LyraType, name: str):
        """Variable identifier construction.

        :param typ: type of the identifier
        :param name: name of the identifier
        """
        super().__init__(typ, name, special=False)
        self._is_high_dimensionality = Status.MAYBE
        self._has_duplicates = Status.MAYBE
        self._is_small = Status.MAYBE
        self._is_shuffled = Status.MAYBE
        self._has_na_values = Status.MAYBE

    @property
    def has_length(self):
        return isinstance(self.typ, (SequenceLyraType, ContainerLyraType))

    @property
    def length(self):
        if self.has_length:
            return LengthIdentifier(self)
        return None

    @property
    def is_dictionary(self):
        return isinstance(self.typ, DictLyraType)

    @property
    def has_keys(self):
        return isinstance(self.typ, DictLyraType)

    @property
    def keys(self):
        if self.has_keys:
            return KeysIdentifier(self)
        return None

    @property
    def has_values(self):
        return isinstance(self.typ, DictLyraType)

    @property
    def values(self):
        if self.has_values:
            return ValuesIdentifier(self)
        return None

    @property
    def is_high_dimensionality(self):
        return self._is_high_dimensionality

    @is_high_dimensionality.setter
    def is_high_dimensionality(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Value must be an instance of Status Enum")
        self._is_high_dimensionality = value

    @property
    def has_duplicates(self):
        return self._has_duplicates

    @has_duplicates.setter
    def has_duplicates(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Value must be an instance of Status Enum")
        self._has_duplicates = value

    @property
    def is_small(self):
        return self._is_small

    @is_small.setter
    def is_small(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Value must be an instance of Status Enum")
        self._is_small = value

    @property
    def is_shuffled(self):
        return self._is_shuffled

    @is_shuffled.setter
    def is_shuffled(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Value must be an instance of Status Enum")
        self._is_shuffled = value

    @property
    def has_na_values(self):
        return self._has_na_values

    @has_na_values.setter
    def has_na_values(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Value must be an instance of Status Enum")
        self._has_na_values = value

class LengthIdentifier(Identifier):
    """Sequence or collection length representation."""

    def __init__(self, expression: Expression):
        """Sequence or collection length construction.

        :param expression: sequence or collection the length of which is being constructed
        """
        name = "len({})".format(expression)
        super().__init__(IntegerLyraType(), name, special=True)
        self._expression = expression

    @property
    def expression(self):
        return self._expression


class KeysIdentifier(Identifier):
    """Dictionary keys identifier representation."""

    def __init__(self, expression: Expression):
        """Dictionary keys identifier construction.

        :param expression: dictionary the keys of which are being identified
        """
        name = "keys({})".format(expression)
        typ = expression.typ
        assert isinstance(typ, DictLyraType)
        super().__init__(typ.key_typ, name, special=True)
        self._expression = expression

    @property
    def expression(self):
        return self._expression


class ValuesIdentifier(Identifier):
    """Dictionary values identifier representation."""

    def __init__(self, expression: Expression):
        """Dictionary values identifier construction.

        :param expression: dictionary the values of which are being identified
        """
        name = "values({})".format(expression)
        typ = expression.typ
        assert isinstance(typ, DictLyraType)
        super().__init__(typ.val_typ, name, special=True)
        self._expression = expression

    @property
    def expression(self):
        return self._expression

class AttributeIdentifier(Identifier):
    """Attribute name identifier representation."""

    def __init__(self, typ: LyraType, name: str):
        """Attribute name identifier construction.

        :param typ: type of the identifier
        :param name: name of the identifier
        """
        super().__init__(typ, name, special=False)

class ListDisplay(Expression):
    """List display representation.

    https://docs.python.org/3/reference/expressions.html#list-displays
    """

    def __init__(self, typ: ListLyraType, items: List[Expression] = None):
        """List display construction.

        :param typ: type of the list
        :param items: list of items being displayed
        """
        super().__init__(typ)
        self._items = items or []

    @property
    def items(self):
        return self._items

    def __eq__(self, other: 'ListDisplay'):
        return (self.typ, self.items) == (other.typ, other.items)

    def __hash__(self):
        return hash((self.typ, str(self.items)))

    def __str__(self):
        items = map(str, self.items)
        return "[" + ", ".join(items) + "]"


class TupleDisplay(Expression):
    """Tuple display (= expression list with comma or ()) representation.

    https://docs.python.org/3/reference/expressions.html#expression-lists
    """

    def __init__(self, typ: TupleLyraType, items: List[Expression] = None):
        """Tuple construction.

        :param typ: type of the tuple
        :param items: list of items being displayed
        """
        super().__init__(typ)
        self._items = items or []

    @property
    def items(self):
        return self._items

    def __eq__(self, other: 'TupleDisplay'):
        return (self.typ, self.items) == (other.typ, other.items)

    def __hash__(self):
        return hash((self.typ, str(self.items)))

    def __str__(self):
        items = map(str, self.items)
        if len(self.items) == 1:
            return f"({next(items)},)"      # add a trailing comma
        return '(' + ', '.join(items) + ')'


class SetDisplay(Expression):
    """Set display representation.

    https://docs.python.org/3/reference/expressions.html#set-displays
    """

    def __init__(self, typ: SetLyraType, items: List[Expression] = None):
        """Set display construction.

        :param typ: type of the set
        :param items: list of items being displayed
        """
        super().__init__(typ)
        self._items = items or []

    @property
    def items(self):
        return self._items

    def __eq__(self, other: 'SetDisplay'):
        return (self.typ, self.items) == (other.typ, other.items)

    def __hash__(self):
        return hash((self.typ, str(self.items)))

    def __str__(self):
        items = map(str, self.items)
        return "{" + ", ".join(items) + "}"


class DictDisplay(Expression):
    """Dictionary display representation.

    https://docs.python.org/3/reference/expressions.html#dictionary-displays
    """

    def __init__(self, typ: DictLyraType, keys: List[Expression] = None,
                 values: List[Expression] = None):
        """Dictionary display construction.

        :param typ: type of the dictionary
        :param keys, values: list of items being displayed (in the form key:value)
        """
        super().__init__(typ)
        self._keys = keys or []
        self._values = values or []

    @property
    def keys(self):
        return self._keys

    @property
    def values(self):
        return self._values

    def __eq__(self, other: 'DictDisplay'):
        return (self.typ, self.keys, self.values) == (other.typ, other.keys, other.values)

    def __hash__(self):
        return hash((self.typ, str(self.keys), str(self.values)))

    def __str__(self):
        keys = map(str, self.keys)
        values = map(str, self.values)
        return '{' + ', '.join(' : '.join(x) for x in zip(keys, values)) + '}'


"""
Primary Expressions
https://docs.python.org/3.4/reference/expressions.html#primaries
"""


class AttributeReference(Expression):
    """Attribute reference representation.

    https://docs.python.org/3.4/reference/expressions.html#attribute-references
    """

    def __init__(self, typ: LyraType, target: Expression, attribute: Identifier):
        """Attribute reference construction.

        :param typ: type of the attribute
        :param target: object the attribute of which is being referenced
        :param attribute: attribute being referenced
        """
        super().__init__(typ)
        self._target = target
        self._attribute = attribute

    @property
    def target(self):
        return self._target

    @property
    def attribute(self):
        return self._attribute

    def __eq__(self, other: 'AttributeReference'):
        typ = self.typ == other.typ
        target = self.target == other.target
        attribute = self.attribute == other.attribute
        return typ and target and attribute

    def __hash__(self):
        return hash((self.typ, self.target, self.attribute))

    def __str__(self):
        return "{0.target}.{0.attribute}".format(self)


class Subscription(Expression):
    """Subscription representation.

    https://docs.python.org/3.4/reference/expressions.html#subscriptions
    """

    def __init__(self, typ: LyraType, target: Expression, key: Expression, is_increasing: Status = Status.MAYBE, is_decreasing: Status = Status.MAYBE):
        """Subscription construction.

        :param typ: type of the subscription
        :param target: object being subject to subscription
        :param key: index at which the object is subscripted
        """
        super().__init__(typ)
        self._target = target
        self._key = key
        self._is_increasing = is_increasing
        self._is_decreasing = is_decreasing

    @property
    def target(self):
        return self._target

    @property
    def key(self):
        return self._key

    @property
    def is_increasing(self):
        return self._is_increasing

    @is_increasing.setter
    def is_increasing(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Value must be an instance of Status Enum")
        self._is_increasing = value

    @property
    def is_decreasing(self):
        return self._is_decreasing

    @is_decreasing.setter
    def is_decreasing(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Value must be an instance of Status Enum")
        self._is_decreasing = value

    def __eq__(self, other: 'Subscription'):
        typ = self.typ == other.typ
        target = self.target == other.target
        key = self.key == other.key
        return typ and target and key

    def __hash__(self):
        top_type = None
        if isinstance(self.typ, list):
            top_type = TopLyraType
        if top_type:
            return hash((top_type, self.target, self.key))
        return hash((self.typ, self.target, self.key))

    def __str__(self):
        return "{0.target}[{0.key}]".format(self)
    
    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        return self.__str__()


class Slicing(Expression):
    """Slicing representation.

    https://docs.python.org/3.4/reference/expressions.html#slicings
    """

    def __init__(self, typ: LyraType, target: Expression,
                 lower: Expression, upper: Expression = None, stride: Expression = None):
        """Slicing construction.

        :param typ: type of the slicing
        :param target: object being subject to slicing
        :param lower: lower bound of the slicing
        :param upper: upper bound of the slicing
        :param stride: stride of the slicing
        """
        super().__init__(typ)
        self._target = target
        self._lower = lower
        self._upper = upper
        self._stride = stride

    @property
    def target(self):
        return self._target

    @property
    def lower(self):
        return self._lower

    @property
    def upper(self):
        return self._upper

    @property
    def stride(self):
        return self._stride

    def __eq__(self, other: 'Slicing'):
        typ = self.typ == other.typ
        target = self.target == other.target
        lower = self.lower == other.lower
        upper = self.upper == other.upper
        stride = self.stride == other.stride
        return typ and target and lower and upper and stride

    def __hash__(self):
        return hash((self.typ, self.target, self.lower, self.upper, self.stride))

    def __str__(self):
        target = "{}[".format(self.target)
        lower = "{}:".format(self.lower)
        upper = "{}".format(self.upper) if self.upper else ""
        stride = ":{}".format(self.stride) if self.stride else ""
        return target + lower + upper + stride + "]"


class Call(Expression, metaclass=ABCMeta):
    """Call representation.

    https://docs.python.org/3.4/reference/expressions.html#calls
    """


class Input(Call):
    """Input call representation."""

    def __init__(self, typ: LyraType):
        """Input call construction.

        :param typ: return type of the input call
        """
        super().__init__(typ)

    def __eq__(self, other: 'Input'):
        return self.typ == other.typ

    def __hash__(self):
        return hash(self.typ)

    def __str__(self):
        return "input()"


class Range(Call):
    """Range call representation."""

    def __init__(self, typ: LyraType, start: Expression, stop: Expression, step: Expression):
        """Range call construction.

        :param typ: return type of the range call
        :param start: start of the range sequence
        :param stop: end of the range sequence (exclusive)
        :param step: difference between elements of the sequence
        """
        super().__init__(typ)
        self._start = start
        self._stop = stop
        self._step = step

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    def __eq__(self, other: 'Range'):
        typ = self.typ == other.typ
        start = self.start == other.start
        stop = self.stop == other.stop
        step = self.step == other.step
        return typ and start and stop and step

    def __hash__(self):
        return hash((self.typ, self.start, self.stop, self.step))

    def __str__(self):
        return f"range({self.start}, {self.stop}, {self.step})"


class Items(Call):
    """Items call representation"""

    def __init__(self, typ: LyraType, target_dict: Expression):
        """Items() call expression construction.

        :param typ: type that items() returns
        :param target_dict: target of the items() call
        """

        super().__init__(typ)
        self._target_dict = target_dict

    @property
    def target_dict(self):
        return self._target_dict

    def __eq__(self, other: 'Items'):
        return (self.typ == other.typ) and (self.target_dict == other.target_dict)

    def __hash__(self):
        return hash((self.typ, str(self.target_dict)))

    def __str__(self):
        return f"{self.target_dict}.items()"


class Keys(Call):
    """Keys call representation"""

    def __init__(self, typ: LyraType, target_dict: Expression):
        """Keys() call expression construction.

        :param typ: type that keys() returns
        :param target_dict: target of the keys() call
        """

        super().__init__(typ)
        self._target_dict = target_dict

    @property
    def target_dict(self):
        return self._target_dict

    def __eq__(self, other: 'Keys'):
        return (self.typ == other.typ) and (self.target_dict == other.target_dict)

    def __hash__(self):
        return hash((self.typ, str(self.target_dict)))

    def __str__(self):
        return f"{self.target_dict}.keys()"


class Values(Call):
    """Values call representation"""

    def __init__(self, typ: LyraType, target_dict: Expression):
        """Values() call expression construction.

        :param typ: type that values() returns
        :param target_dict: target of the values() call
        """

        super().__init__(typ)
        self._target_dict = target_dict

    @property
    def target_dict(self):
        return self._target_dict

    def __eq__(self, other: 'Values'):
        return (self.typ == other.typ) and (self.target_dict == other.target_dict)

    def __hash__(self):
        return hash((self.typ, str(self.target_dict)))

    def __str__(self):
        return f"{self.target_dict}.values()"


"""
Operation Expressions
"""


class Operation(Expression, metaclass=ABCMeta):
    """Operation representation."""


"""
Cast Operation Expressions
"""

class CastOperation(Operation):
    """Cast operation representation."""

    def __init__(self, typ: LyraType, expression: Expression):
        """Cast operation construction.

        :param typ: type of the operation (i.e., the target type of the cast)
        :param expression: expression of the operation (i.e., expression to be cast)
        """
        super().__init__(typ)
        self._expression = expression

    @property
    def expression(self):
        return self._expression

    def __eq__(self, other: 'UnaryOperation'):
        typ = self.typ == other.typ
        expression = self.expression == other.expression
        return typ and expression

    def __hash__(self):
        return hash((self.typ, self.expression))

    def __str__(self):
        expr_string = str(self.expression)
        if isinstance(self.expression, Operation):
            expr_string = f"({expr_string})"
        return f"{str(self.typ)}{expr_string}"


"""
Unary Operation Expressions
"""


class UnaryOperation(Operation):
    """Unary operation representation."""
    class Operator(IntEnum):
        """Unary operator representation."""

        @abstractmethod
        def __str__(self):
            """Unary operator string representation.

            :return: string representing the operator
            """

    def __init__(self, typ: LyraType, operator: Operator, expression: Expression):
        """Unary operation construction.

        :param typ: type of the operation
        :param operator: operator of the operation
        :param expression: expression of the operation
        """
        super().__init__(typ)
        self._operator = operator
        self._expression = expression

    @property
    def operator(self):
        return self._operator

    @property
    def expression(self):
        return self._expression

    def __eq__(self, other: 'UnaryOperation'):
        typ = self.typ == other.typ
        operator = self.operator == other.operator
        expression = self.expression == other.expression
        return typ and operator and expression

    def __hash__(self):
        return hash((self.typ, self.operator, self.expression))

    def __str__(self):
        expr_string = str(self.expression)
        if isinstance(self.expression, Operation):
            expr_string = f"({expr_string})"
        return f"{str(self.operator)}{expr_string}"


class UnaryArithmeticOperation(UnaryOperation):
    """Unary arithmetic operation expression representation.

    https://docs.python.org/3.4/reference/expressions.html#unary-arithmetic-and-bitwise-operations
    """

    class Operator(UnaryOperation.Operator):
        """Unary arithmetic operator representation."""
        Add = 1
        Sub = -1

        def __str__(self):
            if self.value == 1:
                return "+"
            elif self.value == -1:
                return "-"

    def __init__(self, typ: LyraType, operator: Operator, expression: Expression):
        """Unary arithmetic operation expression representation.

        :param typ: type of the operation
        :param operator: operator of the operation
        :param expression: expression of the operation
        """
        super().__init__(typ, operator, expression)


class UnaryBooleanOperation(UnaryOperation):
    """Unary boolean operation expression representation.

    https://docs.python.org/3.4/reference/expressions.html#boolean-operations
    """

    class Operator(UnaryOperation.Operator):
        """Unary boolean operator representation."""
        Neg = 1

        def __str__(self):
            if self.value == 1:
                return "not"

    def __init__(self, typ: LyraType, operator: Operator, expression: Expression):
        """Unary boolean operation expression representation.

        :param typ: type of the operation
        :param operator: operator of the operation
        :param expression: expression of the operation
        """
        super().__init__(typ, operator, expression)


"""
Binary Operation Expressions
"""


class BinaryOperation(Operation):
    """Binary operation representation."""
    class Operator(IntEnum):
        """Binary operator representation."""

        @abstractmethod
        def __str__(self):
            """Binary operator string representation.

            :return: string representing the operator
            """

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression,
                 forloop: bool = False):
        """Binary operation construction.

        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        :param forloop: whether the call happens in a for loop condition (default: False)
        """
        super().__init__(typ)
        self._left = left
        self._operator = operator
        self._right = right
        self._forloop = forloop

    @property
    def left(self):
        return self._left

    @property
    def operator(self):
        return self._operator

    @property
    def right(self):
        return self._right

    @property
    def forloop(self):
        return self._forloop

    def __eq__(self, other: 'BinaryOperation'):
        typ = self.typ == other.typ
        left = self.left == other.left
        operator = self.operator == other.operator
        right = self.right == other.right
        return typ and left and operator and right

    def __hash__(self):
        return hash((self.typ, self.left, self.operator, self.right))

    def __str__(self):
        left_string = str(self.left)
        right_string = str(self.right)
        if isinstance(self.left, Operation):
            left_string = f"({left_string})"
        if isinstance(self.right, Operation):
            right_string = f"({right_string})"
        return f"{left_string} {str(self.operator)} {right_string}"


class BinaryArithmeticOperation(BinaryOperation):
    """Binary arithmetic operation expression representation.

    https://docs.python.org/3.4/reference/expressions.html#binary-arithmetic-operations
    """

    class Operator(BinaryOperation.Operator):
        """Binary arithmetic operator representation."""
        Add = 1
        Sub = 2
        Mult = 3
        Div = 4
        Mod = 5

        def __str__(self):
            if self.value == 1:
                return "+"
            elif self.value == 2:
                return "-"
            elif self.value == 3:
                return "*"
            elif self.value == 4:
                return "/"
            elif self.value == 5:
                return "%"

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary arithmetic operation expression representation.

        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        """
        super().__init__(typ, left, operator, right)


class BinarySequenceOperation(BinaryOperation):
    """Binary sequence operation expression representation."""

    class Operator(BinaryOperation.Operator):
        """Binary sequence operator representation."""
        Concat = 1

        def __str__(self):
            if self.value == 1:
                return "+"

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary sequence operation expression representation.

        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        """
        super().__init__(typ, left, operator, right)


class BinaryBooleanOperation(BinaryOperation):
    """Binary boolean operation expression representation.

    https://docs.python.org/3.6/reference/expressions.html#boolean-operations
    """

    class Operator(BinaryOperation.Operator):
        """Binary arithmetic operator representation."""
        And = 1
        Or = 2

        def reverse_operator(self):
            """Returns the reverse operator of this operator."""
            if self.value == 1:
                return BinaryBooleanOperation.Operator.Or
            elif self.value == 2:
                return BinaryBooleanOperation.Operator.And

        def __str__(self):
            return self.name.lower()

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary boolean operation expression representation.

        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        """
        super().__init__(typ, left, operator, right)


class BinaryComparisonOperation(BinaryOperation):
    """Binary comparison operation expression representation.

    https://docs.python.org/3.4/reference/expressions.html#comparisons
    """

    class Operator(BinaryOperation.Operator):
        """Binary comparison operator representation"""
        Eq = 1
        NotEq = 2
        Lt = 3
        LtE = 4
        Gt = 5
        GtE = 6
        Is = 7
        IsNot = 8
        In = 9
        NotIn = 10

        def reverse_operator(self):
            """Returns the reverse operator of this operator."""
            if self.value == 1:
                return BinaryComparisonOperation.Operator.NotEq
            elif self.value == 2:
                return BinaryComparisonOperation.Operator.Eq
            elif self.value == 3:
                return BinaryComparisonOperation.Operator.GtE
            elif self.value == 4:
                return BinaryComparisonOperation.Operator.Gt
            elif self.value == 5:
                return BinaryComparisonOperation.Operator.LtE
            elif self.value == 6:
                return BinaryComparisonOperation.Operator.Lt
            elif self.value == 7:
                return BinaryComparisonOperation.Operator.IsNot
            elif self.value == 8:
                return BinaryComparisonOperation.Operator.Is
            elif self.value == 9:
                return BinaryComparisonOperation.Operator.NotIn
            elif self.value == 10:
                return BinaryComparisonOperation.Operator.In

        def __str__(self):
            if self.value == 1:
                return "=="
            elif self.value == 2:
                return "!="
            elif self.value == 3:
                return "<"
            elif self.value == 4:
                return "<="
            elif self.value == 5:
                return ">"
            elif self.value == 6:
                return ">="
            elif self.value == 7:
                return "is"
            elif self.value == 8:
                return "is not"
            elif self.value == 9:
                return "in"
            elif self.value == 10:
                return "not in"

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression,
                 forloop: bool = False):
        """Binary comparison operation expression representation.

        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        :param forloop: whether the call happens in a for loop condition (default: False)
        """
        super().__init__(typ, left, operator, right, forloop)


class LambdaExpression(Expression):
    def __init__(self, pp):
        """Lambda expression representation.

        :param args: the formal parameters of the lambda expression
        """
        self._pp = pp

    def __eq__(self, other: 'LambdaExpression'):
        return self._pp == other._pp

    def __hash__(self):
        return hash(self._pp)

    def __str__(self):
        return "LYRA: LAMBDA EXPRESSION NOT REPRESENTED"

class LibraryAccessExpression(Expression):
    def __init__(self, library: str, name: str):
        """Library access expression representation.

        :param library: the library being accessed
        :param name: the function being accessed
        """
        super().__init__(typ=TopLyraType)
        self._library = library
        self._name = name

    @property
    def library(self):
        return self._library

    @property
    def name(self):
        return self._name

    def __eq__(self, other: 'LibraryAccess'):
        return (self.library, self.name) == (other.library, other.name)

    def __hash__(self):
        return hash((self.library, self.name))

    def __str__(self):
        return f"{self.library}.{self.name}"

    def __repr__(self):
        return f"{self.library}.{self.name}"