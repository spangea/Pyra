import itertools
import typing

from lyra.abstract_domains.state import State
from lyra.core.expressions import (
    Input,
    VariableIdentifier,
    ListDisplay,
    Subscription,
    Literal,
    BinaryComparisonOperation,
    BinaryBooleanOperation,
    UnaryOperation, BinaryArithmeticOperation
)

from lyra.core.statements import (
    Call,
    SubscriptionAccess,
    VariableAccess,
    AttributeAccess,
    LibraryAccess,
    ListDisplayAccess,
    Keyword,
    LiteralEvaluation
)

from lyra.engine.forward import ForwardInterpreter


from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice,
)
import warnings
import pandas as pd

from lyra.core.statistical_warnings import (
    GmeanWarning,
    CategoricalConversionMean,
    ScaledMeanWarning,
    CategoricalPlotWarning,
    PCAVisualizationWarning,
    DataLeakage
)

from lyra.semantics.forward import DefaultForwardSemantics
from lyra.semantics.sklearn_statistical_type_semantics import SklearnTypeSemantics
from lyra.semantics.pandas_statistical_type_semantics import PandasStatisticalTypeSemantics
from lyra.semantics.torch_statistical_type_semantics import TorchStatisticalTypeSemantics
from lyra.semantics.seaborn_statistical_type_semantics import SeabornStatisticalTypeSemantics
import lyra.semantics.utilities as utilities
from lyra.semantics.utilities import SelfUtilitiesSemantics
from lyra.semantics.semantics import camel_to_snake
from lyra.semantics.numpy_statistical_type_semantics import NumPyStatisticalTypeSemantics


class StatisticalTypeSemantics(
    DefaultForwardSemantics,
    PandasStatisticalTypeSemantics,
    SklearnTypeSemantics,
    SelfUtilitiesSemantics,
    TorchStatisticalTypeSemantics,
    NumPyStatisticalTypeSemantics,
    SeabornStatisticalTypeSemantics
):
    """Forward semantics of statements with support for Pandas library calls for dataframe column usage analysis."""

    def semantics(self, stmt, state, interpreter, get_caller=False):
        """Override the semantics method to add the get_caller parameter"""
        name = '{}_semantics'.format(camel_to_snake(stmt.__class__.__name__))
        if hasattr(self, name):
            method = getattr(self, name)
            if 'get_caller' in method.__code__.co_varnames:
                return method(stmt, state, interpreter, get_caller=get_caller)
            else:
                return method(stmt, state, interpreter)
        error = f"Semantics for statement {stmt} of type {type(stmt)} not yet implemented! "
        raise NotImplementedError(error + f"You must provide method {name}(...)")

    def relaxed_open_call_policy(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # raise Exception(f"Semantics for {stmt} at line  {stmt.pp.line} not yet implemented")
        state.result = {StatisticalTypeLattice.Status.Top}
        return state

    def dict_call_semantics(self, stmt: Call, state: State, interpreter: ForwardInterpreter) -> State:
        state.result = {StatisticalTypeLattice.Status.Dict}
        return state

    def values_semantics(self, access: AttributeAccess, state: State) -> StatisticalTypeState:
        caller = access.left.variable
        if utilities.is_DataFrame(state, caller) or utilities.is_Series(state, caller):
            return StatisticalTypeLattice.Status.Array
        else:
            return StatisticalTypeLattice.Status.Top

    def attribute_access_semantics(
        self, access: AttributeAccess, state: StatisticalTypeState, interpreter: ForwardInterpreter, is_lhs = False, get_caller = False
    ) -> StatisticalTypeState:
        if is_lhs:
            return {access.left}
        if isinstance(access.target, VariableAccess):
            id = access.target.variable
            # FIXME: Access on fields of df or series can return specific types
            if state.get_type(id) == StatisticalTypeLattice.Status.DataFrame:
                if hasattr(pd.DataFrame, access.attr.name):
                    if access.attr.name == "dtypes":
                        state.result = {StatisticalTypeLattice.Status.Series}
                    elif access.attr.name == "values":
                        state.result = {self.values_semantics(access, state)}
                    else:
                        state.result = {Input(typ=typing.Any)}
                else:
                    state.result = {StatisticalTypeLattice.Status.Series}
            elif StatisticalTypeLattice(state.get_type(id))._less_equal(
                StatisticalTypeLattice(StatisticalTypeLattice.Status.Series)
            ):
                state.result = {Input(typ=typing.Any)}
        elif isinstance(access.target, Call):
            # CHECK
            eval = self.semantics(access.target, state, interpreter)
            for v in eval.variables:
                if v == access.target.arguments[0].variable and isinstance(
                    v, VariableIdentifier
                ):
                    attribute_access = AttributeAccess(
                        state.pp, access.typ, access.target.arguments[0], access.attr
                    )
                    return self.attribute_access_semantics(attribute_access, state, interpreter)
        elif isinstance(access.target, AttributeAccess):
            if access.target.attr.name == "cat":  # Nothing to be done
                if access.attr.name == "codes":
                    state.result = {StatisticalTypeLattice.Status.CatSeries}
        elif isinstance(access.target, LibraryAccess):
            # This should not happen
            raise Exception("Access field is actually a LibraryAccess")
        return state

    def _summarized_view(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        return state.output(dfs)

    def lambda_expression_semantics(self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.relaxed_open_call_policy(stmt, state, interpreter)

    def subscription_access_semantics(
        self,
        stmt: SubscriptionAccess,
        state: StatisticalTypeState,
        interpreter: ForwardInterpreter,
        is_lhs=False,
        get_caller=False,
    ) -> StatisticalTypeState:
        if is_lhs or get_caller: # Left-hand side or get_caller subscription
            # Example: df['column'] = some_value
            if isinstance(stmt, SubscriptionAccess):
                target = stmt.target.variable if isinstance(stmt.target, VariableAccess) else stmt.target
                key = stmt.key.literal if isinstance(stmt.key, LiteralEvaluation) else stmt.key
            else:  # Handle other subscription access types
                # Example: df.loc['index'] = some_value
                target = stmt.left.target.variable if isinstance(stmt.left.target, VariableAccess) else stmt.left.target
                key = stmt.left.key.literal if isinstance(stmt.left.key, LiteralEvaluation) else stmt.left.key

            state.result = {Subscription(stmt.typ if isinstance(stmt, SubscriptionAccess) else stmt.left.typ, target, key)}
            return state

        # Check for AttributeAccess in scenarios like df.loc[0]
        # Example: df.loc[0] or df.iloc[0:5]
        if isinstance(stmt.target, AttributeAccess) and hasattr(
            self, "{}_semantics".format(stmt.target.attr)
        ):
            return getattr(self, "{}_semantics".format(stmt.target.attr))(
                stmt, state, interpreter
            )

        # First, evaluate target and key in the state
        target = self.semantics(stmt.target, state, interpreter).result
        key = self.semantics(stmt.key, state, interpreter).result
        result = set()

        # Sound analysis: if any key is Top, the result should be Top
        # Example: df[some_unknown_variable] where some_unknown_variable is Top
        if any(state.get_type(k) == StatisticalTypeLattice.Status.Top for k in key
            if hasattr(k, 'variable') or isinstance(k, VariableIdentifier)):
            state.result = {StatisticalTypeLattice.Status.Top}
            return state

        for primary, index in itertools.product(target, key):
            # Create a temporary Subscription object for consistent handling
            temp_subscription = Subscription(
                stmt.typ if hasattr(stmt, 'typ') else None,
                primary if not isinstance(primary, StatisticalTypeLattice.Status) else stmt.target,
                index if not isinstance(index, StatisticalTypeLattice.Status) else stmt.key
            )

            # Handle ListDisplay keys - selecting multiple columns
            # Example: df[['col1', 'col2']] - returns a DataFrame with selected columns
            if isinstance(index, ListDisplay):
                if utilities.is_DataFrame(state, primary):
                    result.add(StatisticalTypeLattice.Status.DataFrame)
                else:
                    result.add(temp_subscription)

            # Handle literal or variable keys
            # Examples: df['column'], df[0], array[i] where i is a variable
            elif isinstance(index, (Literal, VariableIdentifier)):
                primary_type = state.get_type(primary)

                if primary_type == StatisticalTypeLattice.Status.DataFrame:
                    # Handle DataFrame access
                    # Example: df[mask] where mask is a boolean array/Series
                    if (isinstance(index, VariableIdentifier) and utilities.is_BoolArray(state, index)):
                        result.add(StatisticalTypeLattice.Status.DataFrame)
                    else:
                        # Example: df['column'] - returns a Series
                        result.add(StatisticalTypeLattice.Status.Series)

                elif utilities.is_Series(state, primary):
                    # Handle Series access
                    # Example: series[0] or series[i] where i is numeric - returns a scalar
                    if (isinstance(index, Literal) and isinstance(index.val, (int, float)) or
                        (isinstance(index.val, str) and index.val.isdigit())) or \
                        (isinstance(index, VariableIdentifier) and utilities.is_Numeric(state, index)):

                        # Determine specific scalar type
                        if utilities.is_NumericSeries(state, primary):
                            # Example: numeric_series[0] - returns a numeric value
                            result.add(StatisticalTypeLattice.Status.Numeric)
                        elif utilities.is_StringSeries(state, primary):
                            # Example: string_series[0] - returns a string
                            result.add(StatisticalTypeLattice.Status.String)
                        elif utilities.is_BoolSeries(state, primary):
                            # Example: bool_series[0] - returns a boolean
                            result.add(StatisticalTypeLattice.Status.Boolean)
                        else:
                            # Example: unknown_type_series[0] - returns a generic scalar
                            result.add(StatisticalTypeLattice.Status.Scalar)
                    else:
                        # Example: series[1:5] - returns a Series
                        result.add(StatisticalTypeLattice.Status.Series)

                # Handle dictionary access
                # Example: my_dict['key']
                elif isinstance(primary, VariableIdentifier) and primary.is_dictionary:
                    result.add(state.values[primary.values].element)
                else:
                    if hasattr(primary, 'variable') or isinstance(primary, VariableIdentifier):
                        # Example: custom_container[key]
                        eval = StatisticalTypeState._evaluation.visit_Subscription(
                            temp_subscription,
                            state,
                            evaluation={}
                        )
                        result.add(eval[temp_subscription].element)
                    else:
                        result.add(primary)

            # Handle boolean expressions for filtering
            # Example: df[df['age'] > 30] or array[x < 5]
            elif isinstance(index, (BinaryComparisonOperation, UnaryOperation, BinaryBooleanOperation)):
                primary_type = state.get_type(primary)
                if primary_type == StatisticalTypeLattice.Status.DataFrame:
                    # Example: df[df['age'] > 30] - returns a filtered DataFrame
                    result.add(StatisticalTypeLattice.Status.DataFrame)
                elif utilities.is_Series(state, primary):
                    # Example: series[series > 0] - returns a filtered Series
                    result.add(StatisticalTypeLattice.Status.Series)
                else:
                    result.add(StatisticalTypeLattice.Status.Top)

            # Handle boolean Series/Array masks
            # Example: df[mask] where mask is a boolean Series/Array
            else:
                index_type = state.get_type(index) if hasattr(index, 'variable') or isinstance(index, VariableIdentifier) else index
                if index_type in (StatisticalTypeLattice.Status.BoolSeries, StatisticalTypeLattice.Status.BoolArray):
                    primary_type = state.get_type(primary)
                    if primary_type == StatisticalTypeLattice.Status.DataFrame:
                        # Example: df[bool_mask] - returns a filtered DataFrame
                        result.add(StatisticalTypeLattice.Status.DataFrame)
                    elif utilities.is_Series(state, primary):
                        # Example: series[bool_mask] - returns a filtered Series
                        result.add(StatisticalTypeLattice.Status.Series)
                    else:
                        result.add(StatisticalTypeLattice.Status.Top)
                elif hasattr(index_type, 'variable') or isinstance(index_type, VariableIdentifier) or isinstance(index_type, StatisticalTypeLattice.Status):
                    # Example: container[unknown_index] where unknown_index could be anything
                    result.add(StatisticalTypeLattice.Status.Top)
                else:
                    error = f"Semantics for subscription of {primary} and {index} (type: {type(index).__name__}) is not yet implemented!"
                    raise NotImplementedError(error)

        state.result = result
        return state

    def min_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # Suppose that min is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function min is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def max_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # Suppose that max is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function max is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def median_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # Suppose that median is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function median is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        caller_to_print = caller if not isinstance(caller, StatisticalTypeLattice.Status) else stmt
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            if caller in state.store and state.get_type(caller) == StatisticalTypeLattice.Status.CatSeries:
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a CatSeries, median my be not meaningful.",
                    category=CategoricalConversionMean,
                    stacklevel=2,
                )
            else:
                if interpreter.warning_level == "possible":
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a CatSeries, median my be not meaningful.",
                        category=CategoricalConversionMean,
                        stacklevel=2,
                    )
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def replace_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def concat_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_axis_eq_1(stmt.arguments):
            state.result = {StatisticalTypeLattice.Status.DataFrame}
        else:
            state.result = {StatisticalTypeLattice.Status.Series}
            for arg in stmt.arguments:
                if isinstance(arg, ListDisplayAccess):
                    for e in arg.items:
                        if utilities.is_DataFrame(state, e):
                            state.result = {
                                StatisticalTypeLattice.Status.DataFrame
                            }
                            break
        return state

    def mean_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # Suppose that mean is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function mean is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        caller_to_print = caller if not isinstance(caller, StatisticalTypeLattice.Status) else stmt
        if utilities.is_Series(state, caller):
            if utilities.is_RatioSeries(state, caller):
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a RatioSeries, gmean should be used.",
                    category=GmeanWarning,
                    stacklevel=2,
                )
            elif utilities.is_CatSeries(state, caller):
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a CatSeries, mean my be not meaningful.",
                    category=CategoricalConversionMean,
                    stacklevel=2,
                )
            elif utilities.is_ScaledSeries(state, caller):
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a ScaledSeries [StdSeries or NormSeries], mean my be not meaningful.",
                    category=ScaledMeanWarning,
                    stacklevel=2,
                )
            else:
                if interpreter.warning_level == "possible":
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a RatioSeries, gmean should be used.",
                        category=GmeanWarning,
                        stacklevel=2,
                    )
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a CatSeries, mean my be not meaningful.",
                        category=CategoricalConversionMean,
                        stacklevel=2,
                    )
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a ScaledSeries [StdSeries or NormSeries], mean my be not meaningful.",
                        category=ScaledMeanWarning,
                        stacklevel=2,
                    )
            state.result = {StatisticalTypeLattice.Status.Numeric}
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def gmean_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # Suppose that gmean is called on a single Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert (
            len(dfs) == 1
        ), "Function gmean is supposed to be called on a single or Series element"
        caller = list(dfs)[0]
        if utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def print_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.NoneRet}
        return state

    def round_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def insert_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.NoneRet}
        return state

    def count_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_List(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def join_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.DataFrame}
        elif utilities.is_String(state, caller):
            state.result = {StatisticalTypeLattice.Status.String}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def split_call_semantics(self, stmt: Call, state: State, interpreter: ForwardInterpreter) -> State:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_String(state, caller):
            state.result = {StatisticalTypeLattice.Status.StringList}
        elif utilities.is_Array(state, caller):
            state.result = {StatisticalTypeLattice.Status.List}
        else:
            state.result = {StatisticalTypeLattice.Status.Top}

        return state

    def abs_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if (
            utilities.is_Series(state, caller)
            or utilities.is_DataFrame(state, caller)
            or utilities.is_Numeric(state, caller)
        ):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def add_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Set(state, caller):
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        else:
            return self._binary_operation(stmt, BinaryArithmeticOperation.Operator.Add, state, interpreter)

    def any_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Boolean}
        return state

    def to_numpy_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Array}
        else:
            state.result = {None}
        return state

    def sum_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_List(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def append_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_List(state, caller):
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def equals_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Boolean}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def len_call_semantics(
        self, stmt: Call, state: State, interpreter: ForwardInterpreter
    ) -> State:
        state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def scatter_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.plot_call_semantics(stmt, state, interpreter)

    def plot_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        for arg in stmt.arguments:
            arg_to_print = arg if not isinstance(arg, StatisticalTypeLattice.Status) else stmt
            if isinstance(arg, Keyword) and arg.name == "data":
                arg_to_print = arg.name
                if interpreter.warning_level == "possible":
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain nominal-scale data, a bar plot should be used.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
            if utilities.is_StringArray(state, arg):
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string array, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_StringList(state, arg):
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string list, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_CatSeries(state, arg):
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a categorical Series, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_StringSeries(state, arg):
                warnings.warn(
                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string Series, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_Array(state, arg) or utilities.is_Series(state, arg) or utilities.is_Top(state, arg):
                if interpreter.warning_level == "possible":
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain nominal-scale data, a bar plot should be used.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
            elif utilities.is_DataFrame(state, arg):
                if isinstance(arg, VariableAccess):
                    arg = arg.variable
                if state.get_type(arg) == StatisticalTypeLattice.Status.DataFrameFromPCA:
                    warnings.warn(
                        f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a DataFrame resulted from PCA, t-SNE or UMAP might be a better choice for visualization.",
                        stacklevel=2,
                    )
                if arg in state.subscriptions:
                    for sub in state.subscriptions[arg]:
                        if utilities.is_CatSeries(state, sub):
                            warnings.warn(
                                f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {sub} is a categorical Series, a bar plot should be used.",
                                category=CategoricalPlotWarning,
                                stacklevel=2,
                            )
                        elif utilities.is_StringSeries(state, sub):
                            warnings.warn(
                                f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> {sub} is a string Series, a bar plot should be used.",
                                category=CategoricalPlotWarning,
                                stacklevel=2,
                            )
        state.result = {StatisticalTypeLattice.Status.Plot}
        return state

    def invert_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller) or utilities.is_Numeric(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        # If caller is a statement return the semantics
        elif isinstance(caller, BinaryComparisonOperation):
            state.result = {caller}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def array_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        eval = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]

        if utilities.is_List(state, eval):
            if utilities.is_NumericList(state,eval):
                state.result = {StatisticalTypeLattice.Status.NumericArray}
            elif utilities.is_StringList(state,eval):
                state.result = {StatisticalTypeLattice.Status.StringArray}
            elif utilities.is_BoolList(state,eval):
                state.result = {StatisticalTypeLattice.Status.BoolArray}
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        else:
            if utilities.is_Numeric(state, eval):
                state.result = {StatisticalTypeLattice.Status.NumericArray}
            elif utilities.is_String(state, eval):
                state.result = {StatisticalTypeLattice.Status.StringArray}
            elif utilities.is_Bool(state, eval):
                state.result = {StatisticalTypeLattice.Status.BoolArray}
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        return state

    def quantile_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]
        first_argument = None
        if len(stmt.arguments) > 1:
            first_argument = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]

        if utilities.is_DataFrame(state, caller):
            if first_argument is None or utilities.is_Numeric(state, first_argument):
                state.result = {StatisticalTypeLattice.Status.Series}
            elif utilities.is_List(state, first_argument) or utilities.is_Series(state, first_argument):
                state.result = {StatisticalTypeLattice.Status.DataFrame}
            else:
                state.result = self.relaxed_open_call_policy(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            if first_argument is None or utilities.is_Numeric(state, first_argument):
                state.result = {StatisticalTypeLattice.Status.Numeric}
            elif utilities.is_List(state, first_argument) or utilities.is_Series(state, first_argument):
                state.result = {StatisticalTypeLattice.Status.Series}
            else:
                state.result = self.relaxed_open_call_policy(stmt, state, interpreter)
        else:
            state.result = self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def tolist_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_StringArray(state, caller):
            state.result = {StatisticalTypeLattice.Status.StringList}
        elif utilities.is_NumericArray(state, caller):
            state.result = {StatisticalTypeLattice.Status.NumericList}
        else:
            state.result = {StatisticalTypeLattice.Status.List}
        return state

    def accuracy_score_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def linspace_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        start = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]
        stop = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]
        dtype = utilities.get_dtype(stmt.arguments)

        if utilities.has_to_retstep(stmt.arguments):
            if (utilities.is_Series(state, start) or utilities.is_Series(state, stop) or
                    utilities.is_List(state, start) or utilities.is_List(state, stop) or
                    utilities.is_Array(state, start) or utilities.is_Array(state, stop)):
                state.result = {(StatisticalTypeLattice.Status.Array,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif dtype is not None:
                if utilities.is_dtype_bool(stmt.arguments):
                    state.result = {(StatisticalTypeLattice.Status.BoolArray,
                                    StatisticalTypeLattice.Status.Numeric)}
                elif utilities.is_dtype_string(stmt.arguments):
                    state.result = {(StatisticalTypeLattice.Status.StringArray,
                                    StatisticalTypeLattice.Status.Numeric)}
                elif utilities.is_dtype_numeric(stmt.arguments):
                    state.result = {(StatisticalTypeLattice.Status.NumericArray,
                                    StatisticalTypeLattice.Status.Numeric)}
                else:
                    state.result = {(StatisticalTypeLattice.Status.Top,
                                    StatisticalTypeLattice.Status.Numeric)}
            else:
                state.result = {(StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.Numeric)}
        else:
            if (utilities.is_Series(state, start) or utilities.is_Series(state, stop) or
                utilities.is_List(state, start) or utilities.is_List(state, stop) or
                utilities.is_Array(state, start) or utilities.is_Array(state, stop)):
                state.result = {StatisticalTypeLattice.Status.Array}
            elif dtype is not None:
                if utilities.is_dtype_bool(stmt.arguments):
                    state.result = {StatisticalTypeLattice.Status.BoolArray}
                elif utilities.is_dtype_string(stmt.arguments):
                    state.result = {StatisticalTypeLattice.Status.StringArray}
                elif utilities.is_dtype_numeric(stmt.arguments):
                    state.result = {StatisticalTypeLattice.Status.NumericArray}
                else:
                    state.result = {StatisticalTypeLattice.Status.Top}
            else:
                state.result = {StatisticalTypeLattice.Status.NumericArray}
        return state

    def union_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Set}
        return state

    def auc_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def format_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.String}
        return state

    def recall_score_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_average_not_None(stmt.arguments):
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.Top}
            else:
                state.result = {StatisticalTypeLattice.Status.Numeric}
        else:
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.Array}
            else:
                state.result = {StatisticalTypeLattice.Status.NumericArray}
        return state

    def precision_score_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_average_not_None(stmt.arguments):
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.Top}
            else:
                state.result = {StatisticalTypeLattice.Status.Numeric}
        else:
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.Array}
            else:
                state.result = {StatisticalTypeLattice.Status.NumericArray}
        return state

    def std_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        dtype = utilities.get_dtype(stmt.arguments)
        booltypes = {"np.bool_", "bool"}

        if (utilities.is_NumericArray(state, caller) or
            utilities.is_NumericList(state, caller) or
            utilities.is_Series(state, caller)):
            if dtype in booltypes:
                state.result = {StatisticalTypeLattice.Status.Boolean}
            else:
                state.result = {StatisticalTypeLattice.Status.Numeric}
        elif utilities.is_Array(state, caller):
            axis = utilities.get_axis(stmt.arguments)
            if axis is None:
                if dtype in booltypes:
                    state.result = {StatisticalTypeLattice.Status.Boolean}
                else:
                    state.result = {StatisticalTypeLattice.Status.Numeric}
            elif 0 <= axis <= 1:
                state.result = {StatisticalTypeLattice.Status.NumericArray}
            elif axis >= 2:
                state.result = {StatisticalTypeLattice.Status.Array}
            else:
                state.result = {StatisticalTypeLattice.Status.Top}
        else:
            state.result = {StatisticalTypeLattice.Status.Top}
        return state

    def interp_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        x = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]

        if utilities.is_Numeric(state, x):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        elif (utilities.is_Series(state, x) or utilities.is_NumericArray(state, x) or
             utilities.is_NumericList(state, x)):
            state.result = {StatisticalTypeLattice.Status.NumericArray}
        else:
            state.result = {StatisticalTypeLattice.Status.Top}
        return state

    def seed_call_semantics(
      self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.NoneRet}
        return state

    def set_option_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.NoneRet}
        return state

    def reset_index_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_DataFrame(state, caller):
            if utilities.is_inplace(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.NoneRet}
            else:
                state.result = {StatisticalTypeLattice.Status.DataFrame}
        elif utilities.is_Series(state, caller):
            if utilities.is_inplace(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.NoneRet}
            else:
                if utilities.has_to_drop(stmt.arguments):
                    state.result = {StatisticalTypeLattice.Status.Series}
                else:
                    state.result = {StatisticalTypeLattice.Status.DataFrame}
        else:
            state.result = {StatisticalTypeLattice.Status.Top}
        return state

    def precision_recall_curve_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {(StatisticalTypeLattice.Status.NumericArray,
                         StatisticalTypeLattice.Status.NumericArray,
                         StatisticalTypeLattice.Status.NumericArray)}
        return state

    def copy_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_List(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def average_precision_score_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def ravel_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_List(state, caller):
            if utilities.is_NumericList(state,caller):
                state.result = {StatisticalTypeLattice.Status.NumericArray}
            elif utilities.is_StringList(state,caller):
                state.result = {StatisticalTypeLattice.Status.StringArray}
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        elif utilities.is_StringArray(state, caller) or utilities.is_NumericArray(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Numeric(state,caller):
            state.result = {StatisticalTypeLattice.Status.NumericArray}
        elif utilities.is_String(state, caller):
            state.result = {StatisticalTypeLattice.Status.StringArray}
        else:
            state.result = {StatisticalTypeLattice.Status.Array}
        return state

    def argmax_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        first_argument = None

        # By default, the index refers to the flattened array. If an axis is specified, the index refers to that dimension.
        if len(stmt.arguments) > 1:
            first_argument = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]

        if first_argument is not None and utilities.is_Numeric(state, first_argument):
            if utilities.is_StringList(state, caller) or utilities.is_NumericList(state, caller):
                state.result = {StatisticalTypeLattice.Status.Numeric}
            else:
                # case where the caller is a ndarray where n > 1
                state.result = {StatisticalTypeLattice.Status.Array}
        else:
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def sorted_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_List(state, caller):
            if utilities.is_StringList(state, caller):
                state.result = {StatisticalTypeLattice.Status.StringList}
            elif utilities.is_NumericList(state, caller):
                state.result = {StatisticalTypeLattice.Status.NumericList}
            else:
                state.result = {StatisticalTypeLattice.Status.List}
        elif utilities.is_Array(state, caller):
            if utilities.is_StringArray(state, caller):
                state.result = {StatisticalTypeLattice.Status.StringList}
            elif utilities.is_NumericArray(state, caller):
                state.result = {StatisticalTypeLattice.Status.NumericList}
            else:
                state.result = {StatisticalTypeLattice.Status.List}
        else:
            state.result = {StatisticalTypeLattice.Status.List}
        return state

    def f1_score_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        average = 'binary' # Default=’binary’
        zero_division = 'warn' # Default='warn'

        if len(stmt.arguments) > 2:
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "average" and arg.value is None:
                    average = arg.value
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "zero_division" and arg.value:
                    zero_division = arg.value

        # If None, the scores for each class are returned
        if average is None:
            if zero_division == "np.nan":
                state.result = {StatisticalTypeLattice.Status.Array}
            else:
                state.result = {StatisticalTypeLattice.Status.NumericArray}
        elif zero_division == "np.nan":
            state.result = {StatisticalTypeLattice.Status.Top}
        else:
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def mean_squared_error_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        multioutput = 'uniform_average'  # Default=’uniform_average’

        if len(stmt.arguments) > 2:
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "multioutput" and arg.value:
                    multioutput = arg.value

        # Returns a full set of errors in case of multioutput input.
        if multioutput == "raw_values":
            state.result = {StatisticalTypeLattice.Status.NumericArray}
        else:
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def confusion_matrix_call_semantics (
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Array}
        return state

    def zeros_like_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        # dtype Overrides the data type of the result.
        if utilities.get_dtype(stmt.arguments) is not None:
            if utilities.is_dtype_string(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.StringArray}
            elif utilities.is_dtype_numeric(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.NumericArray}
            elif utilities.is_dtype_bool(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.BoolArray}
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        else: # The shape and data-type of caller define the same attributes of the returned array.
            if utilities.is_List(state, caller):
                if utilities.is_NumericList(state, caller):
                    state.result = {StatisticalTypeLattice.Status.NumericArray}
                elif utilities.is_StringList(state, caller):
                    state.result = {StatisticalTypeLattice.Status.StringArray}
                elif utilities.is_BoolList(state, caller):
                    state.result = {StatisticalTypeLattice.Status.BoolArray}
                else:
                    state.result = {StatisticalTypeLattice.Status.Array}
            elif utilities.is_Array(state, caller):
                return self.return_same_type_as_caller(stmt, state, interpreter)
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        return state

    def arange_call_semantics (
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:

        first_argument = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]
        second_argument = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]

        if utilities.get_dtype(stmt.arguments) is not None:
            if utilities.is_dtype_bool(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.BoolArray}
            elif utilities.is_dtype_numeric(stmt.arguments):
                state.result = {StatisticalTypeLattice.Status.NumericArray}
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        else:
            if utilities.is_Numeric(state, first_argument) and utilities.is_Numeric(state, second_argument):
                state.result = {StatisticalTypeLattice.Status.NumericArray}
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        return state

    def SVC_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Top}
        return state # Returns an object of the SVC class from the Sklearn library

    def KNeighborsClassifier_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Top}
        return state # Returns an object of the KNeighborsClassifier class from the Sklearn library

    def GaussianNB_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Top}
        return state # Returns an object of the GaussianNB class from the Sklearn library

    def KMeans_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Top}
        return state # Returns an object of the KMeans class from the Sklearn library.

    def RandomizedSearchCV_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Top}
        return state  # Returns an object of the RandomizedSearchCV class from the Sklearn library.

    def RandomForestClassifier_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Top}
        return state # Returns an object of the RandomForestClassifier class from the Sklearn library.

    def GridSearchCV_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Top}
        return state # Returns an object of the GridSearchCV class from the Sklearn library.

    def download_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Boolean}
        return state

    def pop_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_NumericList(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        elif utilities.is_StringList(state, caller):
            state.result = {StatisticalTypeLattice.Status.String}
        elif utilities.is_BoolList(state, caller):
            state.result = {StatisticalTypeLattice.Status.Boolean}
        else:
            state.result = {StatisticalTypeLattice.Status.Top}
        return state

    def train_test_split_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        types: tuple = ()
        for arg in stmt.arguments:
            if not isinstance(arg, Keyword):
                if utilities.is_NormSeries(state, arg):
                    warnings.warn(
                        f"Warning [definite]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be normalized after the split method",
                        category=DataLeakage,
                        stacklevel=2,
                    )
                elif utilities.is_StdSeries(state, arg):
                    warnings.warn(
                        f"Warning [definite]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be standardized after the split method",
                        category=DataLeakage,
                        stacklevel=2,
                    )
                elif utilities.is_CatSeries(state, arg):
                    warnings.warn(
                        f"Warning [definite]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be encoded after the split method",
                        category=DataLeakage,
                        stacklevel=2,
                    )
                elif utilities.is_FeatureSelected(state, arg):
                    warnings.warn(
                        f"Warning [definite]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be Feature Selected after the split method",
                        category=DataLeakage,
                        stacklevel=2,
                    )
                elif utilities.is_Scaled(state, arg):
                    warnings.warn(
                        f"Warning [definite]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be scaled after the split method",
                        category=DataLeakage,
                        stacklevel=2,
                    )
                types += tuple({StatisticalTypeLattice.Status.SplittedTrainData})
                types += tuple({StatisticalTypeLattice.Status.SplittedTestData})
        state.result = {types}
        return state
