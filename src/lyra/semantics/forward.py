"""
Forward Semantics
=================

Lyra's internal forward semantics of statements.

:Authors: Caterina Urban
"""
import typing
import warnings
from abc import ABCMeta
from typing import Union

from lyra.abstract_domains.lattice import EnvironmentMixin
from lyra.core.expressions import BinarySequenceOperation, ListDisplay, VariableIdentifier, \
    SetDisplay, LengthIdentifier, KeysIdentifier, ValuesIdentifier, Subscription
from lyra.core.types import ListLyraType, IntegerLyraType, SetLyraType, SequenceLyraType, \
    ContainerLyraType, DictLyraType
from lyra.engine.interpreter import Interpreter
from lyra.semantics.pandas import DefaultPandasSemantics
from lyra.semantics.semantics import Semantics, DefaultSemantics

from lyra.abstract_domains.state import State
from lyra.core.statements import Assignment, Call, Return, SubscriptionAccess, AccessField

from copy import deepcopy
from lyra.core.statistical_warnings import SpecialSubscriptionAssignmentWarning, SpecialAccessFieldWarning

class ForwardSemantics(Semantics):
    """Forward semantics of statements."""

    def append_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        assert len(stmt.arguments) == 2
        targets = self.semantics(stmt.arguments[0], state, interpreter).result
        op = BinarySequenceOperation.Operator.Concat
        values = self.semantics(stmt.arguments[1], state, interpreter).result
        rhs = set()
        for target in targets:
            for value in values:
                display = ListDisplay(ListLyraType(value.typ), [value])
                rhs.add(BinarySequenceOperation(target.typ, target, op, display))
        return state.assign(targets, rhs)

    def update_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        assert len(stmt.arguments) == 2
        targets = self.semantics(stmt.arguments[0], state, interpreter).result
        op = BinarySequenceOperation.Operator.Concat
        values = self.semantics(stmt.arguments[1], state, interpreter).result
        rhs = set()
        for target in targets:
            for value in values:
                display = SetDisplay(SetLyraType(value.typ), [value])
                rhs.add(BinarySequenceOperation(target.typ, target, op, display))
        return state.assign(targets, rhs)


class UserDefinedCallSemantics(ForwardSemantics):
    """Forward semantics of user-defined function/method calls."""

    def user_defined_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter):
        """Forward semantics of a user-defined function/method call.

        :param stmt: call statement to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """

        # This means that stmt is an open call
        if stmt.name not in interpreter.cfgs:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

        fname, fcfg = stmt.name, interpreter.cfgs[stmt.name]
        # add formal function parameters to the state and assign their actual values
        formal_args = interpreter.fargs[fname]
        for formal, actual in zip(formal_args, stmt.arguments):

            rhs = self.semantics(actual, state, interpreter).result
            state = state.add_variable(formal).forget_variable(formal)
            state = state.assign({formal}, rhs)

            if isinstance(actual, Call) and actual.name in interpreter.cfgs:
                _ret = VariableIdentifier(formal.typ, '{}#return'.format(actual.name))
                state = state.remove_variable(_ret)
        # add local function variables to the state
        _formal_args = set()
        for formal in formal_args:
            _formal_args.add(formal)
            # if isinstance(formal.typ, (SequenceLyraType, ContainerLyraType)):
            #     _formal_args.add(LengthIdentifier(formal))
            #     if isinstance(formal.typ, DictLyraType):
            #         _formal_args.add(KeysIdentifier(formal))
            #         _formal_args.add(ValuesIdentifier(formal))
        local_vars = set(fcfg.variables).difference(_formal_args)
        for local in local_vars:
            state = state.add_variable(local).forget_variable(local)

        fresult = interpreter.analyze(fcfg, state)      # analyze the function
        fstate = fresult.get_node_result(fcfg.out_node)[state][-1]
        state = state.bottom().join(deepcopy(fstate))

        # assign return variable
        if state.result:
            ret = VariableIdentifier(stmt.typ, '{}#return'.format(fname))
            state = state.add_variable(ret).forget_variable(ret)
            state = state.assign({ret}, state.result)
            state.result = {ret}

        # remove local function variables and formal function parameters
        for local in local_vars:
            if not local.special:
                state = state.remove_variable(local)
        for formal in formal_args:
            state = state.remove_variable(formal)

        return state

    def return_semantics(self, stmt: Return, state: State, interpreter: Interpreter):
        """Forward semantics of an return statement.

        :param stmt: return statement to be executed
        :param state: state before executing the return statement
        :return: state modified by the return statement
        """
        if len(stmt.values) != 1:
            error = f"Semantics for multiple arguments of {stmt} is not yet implemented!"
            raise NotImplementedError(error)
        return self.semantics(stmt.values[0], state, interpreter)


class AssignmentSemantics(ForwardSemantics):
    """Forward semantics of assignments."""

    def assignment_semantics(self, stmt: Assignment, state, interpreter) -> State:
        """Forward semantics of an assignment.

        :param stmt: assignment statement to be executed
        :param state: state before executing the assignment
        :return: state modified by the assignment
        """
        if isinstance(stmt.left, AccessField):
            lhs = getattr(self, "access_field_semantics")(stmt, state, interpreter, is_lhs=True)
            warnings.warn(f"Special accessfield in lhs @ line {stmt.pp.line}", SpecialAccessFieldWarning)

        elif (isinstance(stmt.left, SubscriptionAccess) \
                and hasattr(stmt.left.target, "right") and \
                hasattr(self, '{}_semantics'.format(stmt.left.target.right))):
            lhs = {Subscription(typing.Any, stmt.left.target.left, stmt.left.key)}
            warnings.warn(f"Special subscription in lhs @ line {stmt.pp.line}", SpecialSubscriptionAssignmentWarning)
        else:
            lhs = self.semantics(stmt.left, state, interpreter).result      # lhs evaluation

        ret = None
        if isinstance(stmt.right, Call) and stmt.right.name in interpreter.cfgs:
            ret = VariableIdentifier(stmt.right.typ, '{}#return'.format(stmt.right.name))
            state = state.add_variable(ret).forget_variable(ret)

        rhs = self.semantics(stmt.right, state, interpreter).result     # rhs evaluation
        state = state.assign(lhs, rhs)

        if isinstance(stmt.right, Call) and stmt.right.name in interpreter.cfgs:
            state = state.remove_variable(ret)

        return state


# noinspection PyAbstractClass
class DefaultForwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics):
    """Default forward semantics of statements."""
    pass


class DefaultPandasForwardSemantics(DefaultPandasSemantics, UserDefinedCallSemantics, AssignmentSemantics, metaclass=ABCMeta):
    """Default forward semantics of statements with support for Pandas library calls."""
    pass
