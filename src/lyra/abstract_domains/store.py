"""
Store
=====

Lifting of a lattice to a set of program variables.

:Authors: Caterina Urban and Simon Wehrli
"""
import itertools
from collections import defaultdict
from typing import Dict, Any, Type, Set

from lyra.abstract_domains.numerical.interval_lattice import IntervalLattice
from lyra.core.expressions import VariableIdentifier, LengthIdentifier, KeysIdentifier, \
    ValuesIdentifier, Subscription
from lyra.abstract_domains.lattice import Lattice, EnvironmentMixin
from lyra.core.types import LyraType, SequenceLyraType, ContainerLyraType, DictLyraType, \
    IntegerLyraType, DataFrameLyraType
from lyra.core.utils import copy_docstring

import copy

class Store(EnvironmentMixin):
    """Mutable element of a store ``Var -> L``,
    lifting a lattice ``L`` to a set of program variables ``Var``.

    .. warning::
        Lattice operations modify the current store.

    .. document private methods
    .. automethod:: Store._less_equal
    .. automethod:: Store._meet
    .. automethod:: Store._join
    """

    def __init__(self, variables: Set[VariableIdentifier],
                 lattices: Dict[LyraType, Type[Lattice]],
                 arguments: Dict[LyraType, Dict[str, Any]] = None):
        """Create a mapping Var -> L from each variable in Var to the corresponding element in L.

        :param variables: set of program variables
        :param lattices: dictionary from variable types to the corresponding lattice types
        :param arguments: dictionary from variable types to arguments of the corresponding lattices
        """
        super().__init__()
        self._variables = variables
        self._lattices = lattices
        self._arguments = defaultdict(lambda: dict()) if arguments is None else arguments
        try:
            self._store = {v: lattices[v.typ](**self._arguments[v.typ]) for v in variables}
            self._lengths, self._keys, self._values = dict(), dict(), dict()
            for v in variables:
                if v.has_length:
                    self._lengths[v.length] = IntervalLattice(lower=0)
                    if v.is_dictionary:
                        _key = lattices[v.typ.key_typ](**self._arguments[v.typ.key_typ])
                        self._keys[v.keys] = _key
                        _value = lattices[v.typ.val_typ](**self._arguments[v.typ.val_typ])
                        self._values[v.values] = _value
        except KeyError as key:
            error = f"Missing lattice for variable type {repr(key.args[0])}!"
            raise ValueError(error)

    @property
    def variables(self):
        """Variables of the current store."""
        return self._variables

    @property
    def lattices(self):
        """Current dictionary from variable types to the corresponding lattice types."""
        return self._lattices

    @property
    def arguments(self):
        """Current dictionary from variable types to argument of the corresponding lattices."""
        return self._arguments

    @property
    def store(self):
        """Current mapping from variables to their corresponding lattice element."""
        return self._store

    @property
    def lengths(self):
        """Current mapping from variable lengths to their corresponding lattice element."""
        return self._lengths

    @property
    def keys(self):
        """Current mapping from variable keys to their corresponding lattice element."""
        return self._keys

    @property
    def values(self):
        """Current mapping from variable values to their corresponding lattice element."""
        return self._values

    def __repr__(self):
        _store = self.store.items()
        _lengths, _keys, _values = self.lengths.items(), self.keys.items(), self.values.items()
        chain = itertools.chain(_store, _lengths, _keys, _values)
        items = sorted(chain, key=lambda x: x[0].name)
        return "; ".join("{} -> {}".format(variable, value) for variable, value in items if not isinstance(variable, LengthIdentifier))

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'Store':
        for var in self.store:
            self.store[var].bottom()
        for var in self.lengths:
            self.lengths[var].bottom()
        for var in self.keys:
            self.keys[var].bottom()
        for var in self.values:
            self.values[var].bottom()
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'Store':
        for var in self.store:
            self.store[var].top()
        for var in self.lengths:
            self.lengths[var] = IntervalLattice(lower=0)
        for var in self.keys:
            self.keys[var].top()
        for var in self.values:
            self.values[var].top()
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        """The current store is bottom if `any` of its variables map to a bottom element."""
        for variable, element in self.store.items():
            # GD: TEMPORARY FIX
            if not isinstance(variable, Subscription):  # This could happen if lhs is a subscription of a DataFrame
                if hasattr(variable, "has_lenght") and not variable.has_length and element.is_bottom():
                    return True
                elif element.is_bottom():
                    return True
        return any(element.is_bottom() for element in self.lengths.values())

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        """The current store is top if `all` of its variables map to a top element."""
        _store = all(element.is_top() for element in self.store.values())
        _top = IntervalLattice(lower=0)
        _lengths = all(_top.less_equal(element) for element in self.lengths.values())
        return _store and _lengths

    @copy_docstring(EnvironmentMixin.unify)
    def unify(self, other: 'Store'):
        for variable in other.variables:
            if variable not in self.variables:
                self.add_variable(variable)
        return self

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'Store') -> bool:
        """The comparison is performed point-wise for each variable."""
        _store = all(self.store[var].less_equal(other.store[var]) for var in self.store)
        _lengths = all(self.lengths[var].less_equal(other.lengths[var]) for var in self.lengths)
        _keys = all(self.keys[var].less_equal(other.keys[var]) for var in self.keys)
        _values = all(self.values[var].less_equal(other.values[var]) for var in self.values)
        return _store and _lengths and _keys and _values

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'Store'):
        """The meet is performed point-wise for each variable."""
        for var in self.store:
            self.store[var].meet(other.store[var])
        for var in self.lengths:
            self.lengths[var].meet(other.lengths[var])
        for var in self.keys:
            self.keys[var].meet(other.keys[var])
        for var in self.values:
            self.values[var].meet(other.values[var])
        return self

    @copy_docstring(Lattice._join)
    def _join(self, other: 'Store') -> 'Store':
        """The join is performed point-wise for each variable,
        if a variable is not in one of the store,
        it will be added it."""

        # Get variables in store
        store_vars = set(self.store.keys())
        other_vars = set(other.store.keys())
        length_vars = set(self.lengths.keys())
        other_length_vars = set(other.lengths.keys())
        key_vars = set(self.keys.keys())
        other_key_vars = set(other.keys.keys())
        value_vars = set(self.values.keys())
        other_value_vars = set(other.values.keys())

        # Add relative missing variables to both self and other
        for var in other_vars - store_vars:
            self.store[var] = copy.deepcopy(other.store[var])
        for var in other_length_vars - length_vars:
            self.lengths[var] = copy.deepcopy(other.lengths[var])
        for var in other_key_vars - key_vars:
            self.keys[var] = copy.deepcopy(other.keys[var])
        for var in other_value_vars - value_vars:
            self.values[var] = copy.deepcopy(other.values[var])

        for var in store_vars - other_vars:
            other.store[var] = copy.deepcopy(self.store[var])
        for var in length_vars - other_length_vars:
            other.lengths[var] = copy.deepcopy(self.lengths[var])
        for var in key_vars - other_key_vars:
            other.keys[var] = copy.deepcopy(self.keys[var])
        for var in value_vars - other_value_vars:
            other.values[var] = copy.deepcopy(self.values[var])

        for var in self.store:
            self.store[var].join(other.store[var])
        for var in self.lengths:
            self.lengths[var].join(other.lengths[var])
        for var in self.keys:
            self.keys[var].join(other.keys[var])
        for var in self.values:
            self.values[var].join(other.values[var])
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'Store'):
        """The widening is performed point-wise for each variable."""
        for var in self.store:
            self.store[var].widening(other.store[var])
        for var in self.lengths:
            self.lengths[var].widening(other.lengths[var])
        for var in self.keys:
            self.keys[var].widening(other.keys[var])
        for var in self.values:
            self.values[var].widening(other.values[var])
        return self

    @copy_docstring(EnvironmentMixin.add_variable)
    def add_variable(self, variable: VariableIdentifier):
        self.variables.add(variable)
        typ = variable.typ
        self.store[variable] = self.lattices[typ](**self.arguments[typ]).bottom()
        if variable.has_length:
            self.lengths[variable.length] = IntervalLattice(lower=0).bottom()
            if variable.is_dictionary:
                _key = self.lattices[typ.key_typ](**self._arguments[typ.key_typ]).bottom()
                self._keys[variable.keys] = _key
                _value = self.lattices[typ.val_typ](**self._arguments[typ.val_typ]).bottom()
                self._values[variable.values] = _value
        return self

    @copy_docstring(EnvironmentMixin.remove_variable)
    def remove_variable(self, variable: VariableIdentifier):
        self.variables.remove(variable)
        del self.store[variable]
        if variable.has_length:
            del self.lengths[variable.length]
            if variable.is_dictionary:
                del self.keys[variable.keys]
                del self.values[variable.values]
        return self
