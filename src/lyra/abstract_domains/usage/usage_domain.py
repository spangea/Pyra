"""
Syntactic Usage Abstract Domain
===============================

Abstract domain to be used for **input data usage analysis** using syntactic variable dependencies.
A program variable can have value *U* (used), *S* (scoped), *W* (written), and *N* (not used).

:Authors: Caterina Urban and Simon Wehrli
"""
from collections import defaultdict
from copy import deepcopy
from typing import Dict, Type, Set

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.abstract_domains.usage.usage_lattice import UsageLattice
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing, \
    BinaryComparisonOperation, KeysIdentifier, ValuesIdentifier, TupleDisplay
from lyra.core.types import LyraType, DictLyraType
from lyra.core.utils import copy_docstring


class UsageStore(Store):
    """An element of a store mapping each program variable to its usage status.

    All program variables are *not used* by default.

    .. document private methods
    .. automethod:: UsageStore._less_equal
    .. automethod:: UsageStore._meet
    .. automethod:: UsageStore._join
    """

    def __init__(self, variables, lattices: Dict[LyraType, Type[Lattice]]):
        """Map each program variable to its usage status.

        :param variables: set of program variables
        :param lattices: dictionary from variable types to the corresponding lattice types
        """
        super().__init__(variables, lattices)

    @copy_docstring(Store.is_bottom)
    def is_bottom(self) -> bool:
        """The current store is bottom if `all` of its variables map to a bottom element."""
        return all(element.is_bottom() for element in self.store.values())

    def increase(self) -> 'UsageStore':
        """Increase the nesting level.

        :return: current lattice element modified to reflect an increased nesting level

        The increase is performed point-wise for each variable.
        """
        for var in self.store:
            self.store[var].increase()
        return self

    def decrease(self, other: 'UsageStore') -> 'UsageStore':
        """Decrease the nesting level by combining lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to reflect a decreased nesting level

        The decrease is performed point-wise for each variable.
        """
        for var in self.store:
            self.store[var].decrease(other.store[var])
        return self


class SimpleUsageStore(UsageStore):
    """An element of a store mapping each program variable to its usage status.

    All program variables are *not used* by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: SimpleUsageStore._less_equal
    .. automethod:: SimpleUsageStore._meet
    .. automethod:: SimpleUsageStore._join
    """

    def __init__(self, variables: Set[VariableIdentifier]):
        """Map each program variable to its usage status.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: UsageLattice)
        super().__init__(variables, lattices)


class SimpleUsageState(Stack, State):
    """Input data usage analysis state.
    An element of the syntactic usage abstract domain.

    Stack of maps from each program variable to its usage status.
    The stack contains a single map by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: SimpleUsageState._assign
    .. automethod:: SimpleUsageState._assume
    .. automethod:: SimpleUsageState._output
    .. automethod:: SimpleUsageState._substitute
    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__(SimpleUsageStore, {'variables': variables})
        State.__init__(self, precursory)

    @copy_docstring(Stack.push)
    def push(self):
        if self.is_bottom() or self.is_top():
            return self
        self.stack.append(deepcopy(self.lattice).increase())
        return self

    @copy_docstring(Stack.pop)
    def pop(self):
        if self.is_bottom() or self.is_top():
            return self
        current = self.stack.pop()
        self.lattice.decrease(current)
        return self

    def _assign_any(self, left: Expression, right: Expression):
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'SimpleUsageState':
        return self._assign_any(left, right)

    @copy_docstring(State._assign_tuple)
    def _assign_tuple(self, left: TupleDisplay, right: Expression) -> '':
        return self._assign_any(left, right)

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'SimpleUsageState':
        return self._assign_any(left, right)

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'SimpleUsageState':
        return self._assign_any(left, right)

    def _assume_any(self, condition: Expression) -> 'SimpleUsageState':
        effect = False  # effect of the current nesting level on the outcome of the program
        for variable in self.lattice.variables:
            value = self.lattice.store[variable]
            if value.is_written() or value.is_top():
                effect = True
                break
        if effect:  # the current nesting level has an effect on the outcome of the program
            for identifier in condition.ids():
                self.lattice.store[identifier].top()
                if identifier.is_dictionary:
                    self.lattice.keys[identifier.keys].top()
                    self.lattice.values[identifier.values].top()
        return self

    @copy_docstring(State._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_noteq_comparison)
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)
    
    @copy_docstring(State._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'SimpleUsageState':
        return self.push()

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'SimpleUsageState':
        return self.pop()

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'SimpleUsageState':
        return self.push()

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'SimpleUsageState':
        return self.pop()

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier) -> 'State':
        self.lattice.store[variable].bottom()
        if variable.is_dictionary:
            self.lattice.keys[variable.keys].bottom()
            self.lattice.values[variable.values].bottom()
        return self

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'SimpleUsageState':
        for identifier in output.ids():
            self.lattice.store[identifier].top()
            if identifier.is_dictionary:
                self.lattice.keys[identifier.keys].top()
                self.lattice.values[identifier.values].top()
        return self

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'SimpleUsageState':
        if self.lattice.store[left].is_top() or self.lattice.store[left].is_scoped():
            # the assigned variable is used or scoped
            self.lattice.store[left].written()
            if left.is_dictionary:
                self.lattice.keys[left.keys].written()
                self.lattice.values[left.values].written()
            for identifier in right.ids():
                self.lattice.store[identifier].top()
                if identifier.is_dictionary:
                    self.lattice.keys[identifier.keys].top()
                    self.lattice.values[identifier.values].top()
        return self

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'SimpleUsageState':
        target = left.target
        if self.lattice.store[target].is_top() or self.lattice.store[target].is_scoped():
            # the assigned variable is used or scoped
            self.lattice.store[target].top()  # summarization abstraction (join of U/S with W)
            if isinstance(target.typ, DictLyraType):
                self.lattice.keys[KeysIdentifier(target)].top()
                self.lattice.values[ValuesIdentifier(target)].top()
            for identifier in right.ids():
                self.lattice.store[identifier].top()
                if identifier.is_dictionary:
                    self.lattice.keys[identifier.keys].top()
                    self.lattice.values[identifier.values].top()
            ids = left.key.ids()
            for identifier in ids:  # make ids in subscript used
                self.lattice.store[identifier].top()
                if isinstance(identifier.typ, DictLyraType):
                    self.lattice.keys[identifier.keys].top()
                    self.lattice.values[identifier.values].top()
        return self

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'SimpleUsageState':
        target = left.target
        if self.lattice.store[target].is_top() or self.lattice.store[target].is_scoped():
            # the assigned variable is used or scoped
            self.lattice.store[target].top()  # summarization abstraction (join of U/S with W)
            if isinstance(target.typ, DictLyraType):
                self.lattice.keys[KeysIdentifier(target)].top()
                self.lattice.values[ValuesIdentifier(target)].top()
            for identifier in right.ids():
                self.lattice.store[identifier].top()
                if identifier.is_dictionary:
                    self.lattice.store[identifier.keys].top()
                    self.lattice.store[identifier.values].top()
            ids = left.lower.ids() | left.upper.ids()
            for identifier in ids:  # make ids in subscript used
                self.lattice.store[identifier].top()
                if identifier.is_dictionary:
                    self.lattice.keys[identifier.keys].top()
                    self.lattice.values[identifier.values].top()
        return self
