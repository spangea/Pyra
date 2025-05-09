import itertools
import typing

from lyra.abstract_domains.state import State
from lyra.core.expressions import (
    VariableIdentifier,
    ListDisplay,
    Subscription,
    Literal,
    BinaryComparisonOperation,
    BinaryBooleanOperation,
    UnaryOperation, BinaryArithmeticOperation,
    Slicing, LibraryAccessExpression
)

from lyra.core.statements import (
    Call,
    SubscriptionAccess,
    VariableAccess,
    AttributeAccess,
    LibraryAccess,
    ListDisplayAccess,
    Keyword,
    LiteralEvaluation,
    SlicingAccess
)

from lyra.engine.forward import ForwardInterpreter


from lyra.datascience.datascience_type_domain import (
    DatascienceTypeState,
    DatascienceTypeLattice,
)
import warnings
import pandas as pd

from lyra.core.datascience_warnings import (
    GmeanWarning,
    CategoricalConversionMeanWarning,
    ScaledMeanWarning,
    CategoricalPlotWarning,
    PCAVisualizationWarning,
    DataLeakageWarning,
    ReproducibilityWarning
)

from lyra.semantics.forward import DefaultForwardSemantics
from lyra.semantics.sklearn_datascience_type_semantics import SklearnTypeSemantics
from lyra.semantics.pandas_datascience_type_semantics import PandasDatascienceTypeSemantics
from lyra.semantics.torch_datascience_type_semantics import TorchDatascienceTypeSemantics
from lyra.semantics.seaborn_datascience_type_semantics import SeabornDatascienceTypeSemantics
import lyra.semantics.utilities as utilities
from lyra.semantics.utilities import SelfUtilitiesSemantics
from lyra.semantics.semantics import camel_to_snake
from lyra.semantics.numpy_datascience_type_semantics import NumPyDatascienceTypeSemantics

from lyra.core.types import TopLyraType

from lyra.core.expressions import CastOperation, SetDisplay
from lyra.core.types import DictLyraType, ListLyraType, SetLyraType, StringLyraType, TupleLyraType
class DatascienceTypeSemantics(
    DefaultForwardSemantics,
    PandasDatascienceTypeSemantics,
    SklearnTypeSemantics,
    SelfUtilitiesSemantics,
    TorchDatascienceTypeSemantics,
    NumPyDatascienceTypeSemantics,
    SeabornDatascienceTypeSemantics
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
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # raise Exception(f"Semantics for {stmt} at line  {stmt.pp.line} not yet implemented")
        state.result = {DatascienceTypeLattice.Status.Top}
        return state

    def library_access_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if stmt.library == "numpy" and stmt.name == "nan":
            state.result = {DatascienceTypeLattice.Status.Scalar}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def dict_call_semantics(self, stmt: Call, state: State, interpreter: ForwardInterpreter) -> State:
        state.result = {DatascienceTypeLattice.Status.Dict}
        return state

    def values_semantics(self, access: AttributeAccess, state: State,) -> DatascienceTypeState:
        caller = access.target.variable
        if utilities.is_DataFrame(state, caller) or utilities.is_Series(state, caller):
            return DatascienceTypeLattice.Status.Array
        else:
            return self.relaxed_open_call_policy(None, state, None)

    def attribute_access_semantics(
        self, access: AttributeAccess, state: DatascienceTypeState, interpreter: ForwardInterpreter, is_lhs = False, get_caller = False
    ) -> DatascienceTypeState:
        if is_lhs or get_caller:
            if hasattr(access, "left"):
                state.result = {access.left} # Necessary to handle get_caller
                return {access.left}
            state.result = {access}
            return state
        if isinstance(access.target, VariableAccess):
            id = access.target.variable
            # FIXME: Access on fields of df or series can return specific types
            if state.get_type(id) == DatascienceTypeLattice.Status.DataFrame:
                if hasattr(pd.DataFrame, access.attr.name):
                    if access.attr.name == "dtypes":
                        state.result = {DatascienceTypeLattice.Status.Series}
                    elif access.attr.name == "values":
                        state.result = {self.values_semantics(access, state)}
                    else:
                        state.result = {DatascienceTypeLattice.Status.Top}
                else:
                    state.result = {DatascienceTypeLattice.Status.Series}
            elif DatascienceTypeLattice(state.get_type(id))._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)
            ):
                state.result = {DatascienceTypeLattice.Status.Top}
        elif isinstance(access.target, Call):
            # CHECK
            eval = self.semantics(access.target, state, interpreter)
            for v in eval.variables:
                if hasattr(v, "variable") and v.variable == access.target:
                    if v == access.target.arguments[0].variable and isinstance(
                        v, VariableIdentifier
                    ):
                        attribute_access = AttributeAccess(
                            state.pp, access.typ, access.target.arguments[0], access.attr
                        )
                        return self.attribute_access_semantics(attribute_access, state, interpreter)
                else:  # subscriptionaccess
                    if isinstance(v, SubscriptionAccess) and v == access.target.arguments[0]:
                        subscription_access = SubscriptionAccess(
                            state.pp, access.typ, v, access.attr
                        )
                        return self.subscription_access_semantics(subscription_access, state, interpreter)
        elif isinstance(access.target, AttributeAccess):
            if access.target.attr.name == "cat":  # Nothing to be done
                if access.attr.name == "codes":
                    state.result = {DatascienceTypeLattice.Status.CatSeries}
        elif isinstance(access.target, LibraryAccess):
            # This should not happen
            raise Exception("Access field is actually a LibraryAccess")
        else:
            return self.relaxed_open_call_policy(None, state, interpreter)
        return state

    def _summarized_view(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        return state.output(dfs)

    def lambda_expression_semantics(self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.relaxed_open_call_policy(stmt, state, interpreter)

    def subscription_access_semantics(
        self,
        stmt: SubscriptionAccess,
        state: DatascienceTypeState,
        interpreter: ForwardInterpreter,
        is_lhs=False,
        get_caller=False,
    ) -> DatascienceTypeState:
        if is_lhs or get_caller: # Left-hand side or get_caller subscription
            # Example: df['column'] = some_value
            if isinstance(stmt, SubscriptionAccess):
                target = stmt.target.variable if isinstance(stmt.target, VariableAccess) else stmt.target
                if isinstance(target, LibraryAccess):
                    target = LibraryAccessExpression(target.library, target.name)
                key = stmt.key.literal if isinstance(stmt.key, LiteralEvaluation) else stmt.key
            else:  # Handle other subscription access types
                # Example: df.loc['index'] = some_value
                target = stmt.left.target.variable if isinstance(stmt.left.target, VariableAccess) else stmt.left.target
                key = stmt.left.key.literal if isinstance(stmt.left.key, LiteralEvaluation) else stmt.left.key

            state.result = {Subscription(TopLyraType, target, key)}
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
        if any(state.get_type(k) == DatascienceTypeLattice.Status.Top for k in key
            if hasattr(k, 'variable') or isinstance(k, VariableIdentifier)):
            state.result = {DatascienceTypeLattice.Status.Top}
            return state

        for primary, index in itertools.product(target, key):
            # Create a temporary Subscription object for consistent handling
            temp_subscription = Subscription(
                TopLyraType,
                primary if not isinstance(primary, DatascienceTypeLattice.Status) else stmt.target,
                index if not isinstance(index, DatascienceTypeLattice.Status) else stmt.key
            )

            # Handle ListDisplay keys - selecting multiple columns
            # Example: df[['col1', 'col2']] - returns a DataFrame with selected columns
            if isinstance(index, ListDisplay):
                if utilities.is_DataFrame(state, primary):
                    result.add(DatascienceTypeLattice.Status.DataFrame)
                else:
                    result.add(temp_subscription)

            # Handle literal or variable keys
            # Examples: df['column'], df[0], array[i] where i is a variable
            elif isinstance(index, (Literal, VariableIdentifier)):
                primary_type = state.get_type(primary)

                if primary_type == DatascienceTypeLattice.Status.DataFrame:
                    # Handle DataFrame access
                    # Example: df[mask] where mask is a boolean array/Series
                    if (isinstance(index, VariableIdentifier) and utilities.is_BoolArray(state, index)):
                        result.add(DatascienceTypeLattice.Status.DataFrame)
                    else:
                        # Example: df['column'] - returns a Series
                        result.add(DatascienceTypeLattice.Status.Series)

                elif utilities.is_Series(state, primary):
                    # Handle Series access
                    # Example: series[0] or series[i] where i is numeric - returns a scalar
                    if (isinstance(index, Literal) and isinstance(index.val, (int, float)) or
                        (isinstance(index.val, str) and index.val.isdigit())) or \
                        (isinstance(index, VariableIdentifier) and utilities.is_Numeric(state, index)):

                        # Determine specific scalar type
                        if utilities.is_NumericSeries(state, primary):
                            # Example: numeric_series[0] - returns a numeric value
                            result.add(DatascienceTypeLattice.Status.Numeric)
                        elif utilities.is_StringSeries(state, primary):
                            # Example: string_series[0] - returns a string
                            result.add(DatascienceTypeLattice.Status.String)
                        elif utilities.is_BoolSeries(state, primary):
                            # Example: bool_series[0] - returns a boolean
                            result.add(DatascienceTypeLattice.Status.Boolean)
                        else:
                            # Example: unknown_type_series[0] - returns a generic scalar
                            result.add(DatascienceTypeLattice.Status.Scalar)
                    else:
                        # Example: series[1:5] - returns a Series
                        result.add(DatascienceTypeLattice.Status.Series)

                # Handle dictionary access
                # Example: my_dict['key']
                elif isinstance(primary, VariableIdentifier) and primary.is_dictionary:
                    result.add(state.values[primary.values].element)
                else:
                    if hasattr(primary, 'variable') or isinstance(primary, VariableIdentifier):
                        # Example: custom_container[key]
                        eval = DatascienceTypeState._evaluation.visit_Subscription(
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
                if primary_type == DatascienceTypeLattice.Status.DataFrame:
                    # Example: df[df['age'] > 30] - returns a filtered DataFrame
                    result.add(DatascienceTypeLattice.Status.DataFrame)
                elif utilities.is_Series(state, primary):
                    # Example: series[series > 0] - returns a filtered Series
                    result.add(DatascienceTypeLattice.Status.Series)
                else:
                    result.add(DatascienceTypeLattice.Status.Top)

            # Handle boolean Series/Array masks
            # Example: df[mask] where mask is a boolean Series/Array
            else:
                index_type = state.get_type(index) if hasattr(index, 'variable') or isinstance(index, VariableIdentifier) else index
                if index_type in (DatascienceTypeLattice.Status.BoolSeries, DatascienceTypeLattice.Status.BoolArray):
                    primary_type = state.get_type(primary)
                    if primary_type == DatascienceTypeLattice.Status.DataFrame:
                        # Example: df[bool_mask] - returns a filtered DataFrame
                        result.add(DatascienceTypeLattice.Status.DataFrame)
                    elif utilities.is_Series(state, primary):
                        # Example: series[bool_mask] - returns a filtered Series
                        result.add(DatascienceTypeLattice.Status.Series)
                    else:
                        result.add(DatascienceTypeLattice.Status.Top)
                elif hasattr(index_type, 'variable') or isinstance(index_type, VariableIdentifier) or isinstance(index_type, DatascienceTypeLattice.Status):
                    # Example: container[unknown_index] where unknown_index could be anything
                    result.add(DatascienceTypeLattice.Status.Top)
                else:
                    error = f"Semantics for subscription of {primary} and {index} (type: {type(index).__name__}) is not yet implemented!"
                    raise NotImplementedError(error)

        state.result = result
        return state

    def min_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # Suppose that min is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function min is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        if utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def max_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # Suppose that max is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function max is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        if utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def median_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # Suppose that median is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function median is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        caller_to_print = caller if not isinstance(caller, DatascienceTypeLattice.Status) else stmt
        if utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            if caller in state.store and state.get_type(caller) == DatascienceTypeLattice.Status.CatSeries:
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a CatSeries, median my be not meaningful.",
                    category=CategoricalConversionMeanWarning,
                    stacklevel=2,
                )
            else:
                if interpreter.warning_level == "potential":
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a CatSeries, median my be not meaningful.",
                        category=CategoricalConversionMeanWarning,
                        stacklevel=2,
                    )
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def replace_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def concat_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_axis_eq_1(stmt.arguments):
            state.result = {DatascienceTypeLattice.Status.DataFrame}
        else:
            state.result = {DatascienceTypeLattice.Status.Series}
            for arg in stmt.arguments:
                if isinstance(arg, ListDisplayAccess):
                    for e in arg.items:
                        if utilities.is_DataFrame(state, e):
                            state.result = {
                                DatascienceTypeLattice.Status.DataFrame
                            }
                            break
        return state

    def mean_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # Suppose that mean is called either on a single DataFrame or Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert len(dfs) == 1, (
            "Function mean is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        caller_to_print = caller if not isinstance(caller, DatascienceTypeLattice.Status) else stmt
        if utilities.is_Series(state, caller):
            if utilities.is_RatioSeries(state, caller):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a RatioSeries, gmean should be used.",
                    category=GmeanWarning,
                    stacklevel=2,
                )
            elif utilities.is_CatSeries(state, caller):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a CatSeries, mean my be not meaningful.",
                    category=CategoricalConversionMeanWarning,
                    stacklevel=2,
                )
            elif utilities.is_ScaledSeries(state, caller):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} is a ScaledSeries [StdSeries or NormSeries], mean my be not meaningful.",
                    category=ScaledMeanWarning,
                    stacklevel=2,
                )
            else:
                if interpreter.warning_level == "potential":
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a RatioSeries, gmean should be used.",
                        category=GmeanWarning,
                        stacklevel=2,
                    )
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a CatSeries, mean my be not meaningful.",
                        category=CategoricalConversionMeanWarning,
                        stacklevel=2,
                    )
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> if in {caller_to_print} there is a ScaledSeries [StdSeries or NormSeries], mean my be not meaningful.",
                        category=ScaledMeanWarning,
                        stacklevel=2,
                    )
            state.result = {DatascienceTypeLattice.Status.Numeric}
        elif utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def gmean_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # Suppose that gmean is called on a single Series
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        assert (
            len(dfs) == 1
        ), "Function gmean is supposed to be called on a single or Series element"
        caller = list(dfs)[0]
        if utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def print_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def round_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def insert_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def count_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        elif utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_List(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def join_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.DataFrame}
        elif utilities.is_String(state, caller):
            state.result = {DatascienceTypeLattice.Status.String}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def split_call_semantics(self, stmt: Call, state: State, interpreter: ForwardInterpreter) -> State:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_String(state, caller):
            state.result = {DatascienceTypeLattice.Status.StringList}
        elif utilities.is_Array(state, caller):
            state.result = {DatascienceTypeLattice.Status.List}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def abs_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
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
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Set(state, caller):
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        else:
            return self._binary_operation(stmt, BinaryArithmeticOperation.Operator.Add, state, interpreter)

    def any_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Boolean}
        return state

    def to_numpy_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Array}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def sum_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_List(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
            return state
        elif utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def append_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_List(state, caller):
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def equals_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Boolean}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def len_call_semantics(
        self, stmt: Call, state: State, interpreter: ForwardInterpreter
    ) -> State:
        state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def scatter_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.plot_call_semantics(stmt, state, interpreter)

    def scatter_3d_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.plot_call_semantics(stmt, state, interpreter)

    def plot_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        data = None
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "kind" and arg.value in ["bar", "barh"]:
                state.result = {DatascienceTypeLattice.Status.Plot}
                return state

        for arg in stmt.arguments:
            arg_to_print = arg if not isinstance(arg, DatascienceTypeLattice.Status) else stmt
            if isinstance(arg, Keyword) and arg.name == "data":
                arg_to_print = arg.name
                # If the value of the data argument is a DataFrame, raise a warning
                for v in state.variables:
                    if utilities.is_DataFrame(state, v):
                        data = v
                        if interpreter.warning_level == "potential":
                            warnings.warn(
                                f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, a bar plot should be used.",
                                category=CategoricalPlotWarning,
                                stacklevel=2,
                            )
                            break
        if data is None: # Only used in case of positional argument with x, y, z keywords
            tmp_arg = None
            if isinstance(stmt.arguments[0], VariableAccess):
                tmp_arg = stmt.arguments[0].variable
            elif isinstance(stmt.arguments[0], VariableIdentifier):
                tmp_arg = stmt.arguments[0]
            if tmp_arg and utilities.is_DataFrame(state, tmp_arg):
                data = tmp_arg
        for arg in stmt.arguments:
            arg_to_print = arg if not isinstance(arg, DatascienceTypeLattice.Status) else stmt
            if isinstance(arg, Keyword) and arg.name in ["x", "y", "z"]:
                # Check if the argument is a subscription of data
                possible_sub_name = arg.value
                if data and data in state.subscriptions:
                    for sub in state.subscriptions[data]:
                        if sub.key.val == possible_sub_name:
                            if utilities.is_CatSeries(state, sub):
                                warnings.warn(
                                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a categorical Series, a bar plot should be used.",
                                    category=CategoricalPlotWarning,
                                    stacklevel=2,
                                )
                            elif utilities.is_StringSeries(state, sub):
                                warnings.warn(
                                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string Series, a bar plot should be used.",
                                    category=CategoricalPlotWarning,
                                    stacklevel=2,
                                )
                            elif utilities.is_Series(state, sub) and not utilities.is_NumericSeries(state, sub):
                                if interpreter.warning_level == "potential":
                                    warnings.warn(
                                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, a bar plot should be used. ",
                                        category=CategoricalPlotWarning,
                                        stacklevel=2,
                                    )
                            break
                elif interpreter.warning_level == "potential":
                    warnings.warn(
                                f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, a bar plot should be used. ",
                                category=CategoricalPlotWarning,
                                stacklevel=2,
                            )
            if utilities.is_StringArray(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string array, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_StringList(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string list, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_CatSeries(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a categorical Series, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_StringSeries(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string Series, a bar plot should be used.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif (utilities.is_Array(state, arg) or utilities.is_Top(state, arg)) and not utilities.is_NumericArray(state, arg):
                if interpreter.warning_level == "potential":
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, a bar plot should be used. ",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
            elif utilities.is_DataFrame(state, arg):
                if isinstance(arg, VariableAccess):
                    arg = arg.variable
                if state.get_type(arg) == DatascienceTypeLattice.Status.DataFrameFromPCA:
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a DataFrame resulted from PCA, t-SNE or UMAP might be a better choice for visualization.",
                        stacklevel=2,
                        category=PCAVisualizationWarning
                    )
            # Also a subscription to a DataFrameFromPCA a PCAVisualizationWarning must be raised
            elif isinstance(arg, SubscriptionAccess):
                if utilities.is_CatSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a categorical Series, a bar plot should be used.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
                elif utilities.is_StringSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string Series, a bar plot should be used.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
                elif utilities.is_Series(state, arg) and not utilities.is_NumericSeries(state, arg):
                    if interpreter.warning_level == "potential":
                        warnings.warn(
                            f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, a bar plot should be used. ",
                            category=CategoricalPlotWarning,
                            stacklevel=2,
                        )
                if isinstance(arg.target, VariableAccess):
                    arg = arg.target.variable
                else:
                    arg = arg.target
                if state.get_type(arg) == DatascienceTypeLattice.Status.DataFrameFromPCA:
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a DataFrame resulted from PCA, t-SNE or UMAP might be a better choice for visualization.",
                        stacklevel=2,
                        category=PCAVisualizationWarning
                    )
            elif utilities.is_Series(state, arg):
                if utilities.is_CatSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a categorical Series, a bar plot should be used.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
                elif utilities.is_StringSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string Series, a bar plot should be used.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
                elif utilities.is_Series(state, arg) and not utilities.is_NumericSeries(state, arg):
                    if interpreter.warning_level == "potential":
                        warnings.warn(
                            f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, a bar plot should be used. ",
                            category=CategoricalPlotWarning,
                            stacklevel=2,
                        )

        state.result = {DatascienceTypeLattice.Status.Plot}
        return state

    def invert_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
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
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        eval = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]

        if utilities.is_List(state, eval):
            if utilities.is_NumericList(state,eval):
                state.result = {DatascienceTypeLattice.Status.NumericArray}
            elif utilities.is_StringList(state,eval):
                state.result = {DatascienceTypeLattice.Status.StringArray}
            elif utilities.is_BoolList(state,eval):
                state.result = {DatascienceTypeLattice.Status.BoolArray}
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        else:
            if utilities.is_Numeric(state, eval):
                state.result = {DatascienceTypeLattice.Status.NumericArray}
            elif utilities.is_String(state, eval):
                state.result = {DatascienceTypeLattice.Status.StringArray}
            elif utilities.is_Boolean(state, eval):
                state.result = {DatascienceTypeLattice.Status.BoolArray}
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        return state

    def quantile_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]
        first_argument = None
        if len(stmt.arguments) > 1:
            first_argument = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]

        if utilities.is_DataFrame(state, caller):
            if first_argument is None or utilities.is_Numeric(state, first_argument):
                state.result = {DatascienceTypeLattice.Status.Series}
            elif utilities.is_List(state, first_argument) or utilities.is_Series(state, first_argument):
                state.result = {DatascienceTypeLattice.Status.DataFrame}
            else:
                state.result = self.relaxed_open_call_policy(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            if first_argument is None or utilities.is_Numeric(state, first_argument):
                state.result = {DatascienceTypeLattice.Status.Numeric}
            elif utilities.is_List(state, first_argument) or utilities.is_Series(state, first_argument):
                state.result = {DatascienceTypeLattice.Status.Series}
            else:
                state.result = self.relaxed_open_call_policy(stmt, state, interpreter)
        else:
            state.result = self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def tolist_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_StringArray(state, caller):
            state.result = {DatascienceTypeLattice.Status.StringList}
        elif utilities.is_NumericArray(state, caller):
            state.result = {DatascienceTypeLattice.Status.NumericList}
        else:
            state.result = {DatascienceTypeLattice.Status.List}
        return state

    def accuracy_score_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def linspace_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        start = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]
        stop = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]
        dtype = utilities.get_dtype(stmt.arguments)

        if utilities.has_to_retstep(stmt.arguments):
            if (utilities.is_Series(state, start) or utilities.is_Series(state, stop) or
                    utilities.is_List(state, start) or utilities.is_List(state, stop) or
                    utilities.is_Array(state, start) or utilities.is_Array(state, stop)):
                state.result = {(DatascienceTypeLattice.Status.Array,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif dtype is not None:
                if utilities.is_dtype_bool(stmt.arguments):
                    state.result = {(DatascienceTypeLattice.Status.BoolArray,
                                    DatascienceTypeLattice.Status.Numeric)}
                elif utilities.is_dtype_string(stmt.arguments):
                    state.result = {(DatascienceTypeLattice.Status.StringArray,
                                    DatascienceTypeLattice.Status.Numeric)}
                elif utilities.is_dtype_numeric(stmt.arguments):
                    state.result = {(DatascienceTypeLattice.Status.NumericArray,
                                    DatascienceTypeLattice.Status.Numeric)}
                else:
                    state.result = {(DatascienceTypeLattice.Status.Top,
                                    DatascienceTypeLattice.Status.Numeric)}
            else:
                state.result = {(DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.Numeric)}
        else:
            if (utilities.is_Series(state, start) or utilities.is_Series(state, stop) or
                utilities.is_List(state, start) or utilities.is_List(state, stop) or
                utilities.is_Array(state, start) or utilities.is_Array(state, stop)):
                state.result = {DatascienceTypeLattice.Status.Array}
            elif dtype is not None:
                if utilities.is_dtype_bool(stmt.arguments):
                    state.result = {DatascienceTypeLattice.Status.BoolArray}
                elif utilities.is_dtype_string(stmt.arguments):
                    state.result = {DatascienceTypeLattice.Status.StringArray}
                elif utilities.is_dtype_numeric(stmt.arguments):
                    state.result = {DatascienceTypeLattice.Status.NumericArray}
                else:
                    state.result = {DatascienceTypeLattice.Status.Top}
            else:
                state.result = {DatascienceTypeLattice.Status.NumericArray}
        return state

    def union_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Set}
        return state

    def auc_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def format_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.String}
        return state

    def recall_score_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_average_not_None(stmt.arguments):
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.Top}
            else:
                state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.Array}
            else:
                state.result = {DatascienceTypeLattice.Status.NumericArray}
        return state

    def precision_score_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_average_not_None(stmt.arguments):
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.Top}
            else:
                state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            if utilities.is_zero_division_NaN(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.Array}
            else:
                state.result = {DatascienceTypeLattice.Status.NumericArray}
        return state

    def std_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        dtype = utilities.get_dtype(stmt.arguments)
        booltypes = {"np.bool_", "bool"}

        if (utilities.is_NumericArray(state, caller) or
            utilities.is_NumericList(state, caller) or
            utilities.is_Series(state, caller)):
            if dtype in booltypes:
                state.result = {DatascienceTypeLattice.Status.Boolean}
            else:
                state.result = {DatascienceTypeLattice.Status.Numeric}
        elif utilities.is_Array(state, caller):
            axis = utilities.get_axis(stmt.arguments)
            if axis is None:
                if dtype in booltypes:
                    state.result = {DatascienceTypeLattice.Status.Boolean}
                else:
                    state.result = {DatascienceTypeLattice.Status.Numeric}
            elif 0 <= axis <= 1:
                state.result = {DatascienceTypeLattice.Status.NumericArray}
            elif axis >= 2:
                state.result = {DatascienceTypeLattice.Status.Array}
            else:
                state.result = {DatascienceTypeLattice.Status.Top}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def interp_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        x = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]

        if utilities.is_Numeric(state, x):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        elif (utilities.is_Series(state, x) or utilities.is_NumericArray(state, x) or
             utilities.is_NumericList(state, x)):
            state.result = {DatascienceTypeLattice.Status.NumericArray}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def seed_call_semantics(
      self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def set_option_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def reset_index_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_DataFrame(state, caller):
            if utilities.is_inplace(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.NoneRet}
            else:
                state.result = {DatascienceTypeLattice.Status.DataFrame}
        elif utilities.is_Series(state, caller):
            if utilities.is_inplace(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.NoneRet}
            else:
                if utilities.has_to_drop(stmt.arguments):
                    state.result = {DatascienceTypeLattice.Status.Series}
                else:
                    state.result = {DatascienceTypeLattice.Status.DataFrame}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def precision_recall_curve_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {(DatascienceTypeLattice.Status.NumericArray,
                         DatascienceTypeLattice.Status.NumericArray,
                         DatascienceTypeLattice.Status.NumericArray)}
        return state

    def copy_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_List(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def average_precision_score_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def ravel_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_List(state, caller):
            if utilities.is_NumericList(state,caller):
                state.result = {DatascienceTypeLattice.Status.NumericArray}
            elif utilities.is_StringList(state,caller):
                state.result = {DatascienceTypeLattice.Status.StringArray}
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        elif utilities.is_StringArray(state, caller) or utilities.is_NumericArray(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Numeric(state,caller):
            state.result = {DatascienceTypeLattice.Status.NumericArray}
        elif utilities.is_String(state, caller):
            state.result = {DatascienceTypeLattice.Status.StringArray}
        else:
            state.result = {DatascienceTypeLattice.Status.Array}
        return state

    def argmax_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        first_argument = None

        # By default, the index refers to the flattened array. If an axis is specified, the index refers to that dimension.
        if len(stmt.arguments) > 1:
            first_argument = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]

        if first_argument is not None and utilities.is_Numeric(state, first_argument):
            if utilities.is_StringList(state, caller) or utilities.is_NumericList(state, caller):
                state.result = {DatascienceTypeLattice.Status.Numeric}
            else:
                # case where the caller is a ndarray where n > 1
                state.result = {DatascienceTypeLattice.Status.Array}
        else:
            state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def sorted_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_List(state, caller):
            if utilities.is_StringList(state, caller):
                state.result = {DatascienceTypeLattice.Status.StringList}
            elif utilities.is_NumericList(state, caller):
                state.result = {DatascienceTypeLattice.Status.NumericList}
            else:
                state.result = {DatascienceTypeLattice.Status.List}
        elif utilities.is_Array(state, caller):
            if utilities.is_StringArray(state, caller):
                state.result = {DatascienceTypeLattice.Status.StringList}
            elif utilities.is_NumericArray(state, caller):
                state.result = {DatascienceTypeLattice.Status.NumericList}
            else:
                state.result = {DatascienceTypeLattice.Status.List}
        else:
            state.result = {DatascienceTypeLattice.Status.List}
        return state

    def f1_score_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

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
                state.result = {DatascienceTypeLattice.Status.Array}
            else:
                state.result = {DatascienceTypeLattice.Status.NumericArray}
        elif zero_division == "np.nan":
            state.result = {DatascienceTypeLattice.Status.Top}
        else:
            state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def mean_squared_error_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        multioutput = 'uniform_average'  # Default=’uniform_average’

        if len(stmt.arguments) > 2:
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "multioutput" and arg.value:
                    multioutput = arg.value

        # Returns a full set of errors in case of multioutput input.
        if multioutput == "raw_values":
            state.result = {DatascienceTypeLattice.Status.NumericArray}
        else:
            state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def confusion_matrix_call_semantics (
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Array}
        return state

    def zeros_like_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        caller = self.get_caller(stmt, state, interpreter)

        # dtype Overrides the data type of the result.
        if utilities.get_dtype(stmt.arguments) is not None:
            if utilities.is_dtype_string(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.StringArray}
            elif utilities.is_dtype_numeric(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.NumericArray}
            elif utilities.is_dtype_bool(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.BoolArray}
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        else: # The shape and data-type of caller define the same attributes of the returned array.
            if utilities.is_List(state, caller):
                if utilities.is_NumericList(state, caller):
                    state.result = {DatascienceTypeLattice.Status.NumericArray}
                elif utilities.is_StringList(state, caller):
                    state.result = {DatascienceTypeLattice.Status.StringArray}
                elif utilities.is_BoolList(state, caller):
                    state.result = {DatascienceTypeLattice.Status.BoolArray}
                else:
                    state.result = {DatascienceTypeLattice.Status.Array}
            elif utilities.is_Array(state, caller):
                return self.return_same_type_as_caller(stmt, state, interpreter)
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        return state

    def arange_call_semantics (
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:

        first_argument = list(self.semantics(stmt.arguments[0], state, interpreter).result)[0]
        second_argument = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]

        if utilities.get_dtype(stmt.arguments) is not None:
            if utilities.is_dtype_bool(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.BoolArray}
            elif utilities.is_dtype_numeric(stmt.arguments):
                state.result = {DatascienceTypeLattice.Status.NumericArray}
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        else:
            if utilities.is_Numeric(state, first_argument) and utilities.is_Numeric(state, second_argument):
                state.result = {DatascienceTypeLattice.Status.NumericArray}
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        return state

    def SVC_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Top}
        return state # Returns an object of the SVC class from the Sklearn library

    def KNeighborsClassifier_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Top}
        return state # Returns an object of the KNeighborsClassifier class from the Sklearn library

    def GaussianNB_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Top}
        return state # Returns an object of the GaussianNB class from the Sklearn library

    def KMeans_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Top}
        return state # Returns an object of the KMeans class from the Sklearn library.

    def RandomizedSearchCV_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Top}
        return state  # Returns an object of the RandomizedSearchCV class from the Sklearn library.

    def RandomForestClassifier_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Top}
        return state # Returns an object of the RandomForestClassifier class from the Sklearn library.

    def GridSearchCV_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Top}
        return state # Returns an object of the GridSearchCV class from the Sklearn library.

    def download_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Boolean}
        return state

    def pop_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_NumericList(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        elif utilities.is_StringList(state, caller):
            state.result = {DatascienceTypeLattice.Status.String}
        elif utilities.is_BoolList(state, caller):
            state.result = {DatascienceTypeLattice.Status.Boolean}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def train_test_split_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        is_reproducible = False
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "random_state":
                is_reproducible = True
                break
        if not is_reproducible:
            warnings.warn(
                f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} the random state is not set, the experiment might not be reproducible.",
                category=ReproducibilityWarning,
                stacklevel=2,
            )
        types: tuple = ()
        for arg in stmt.arguments:
            if not isinstance(arg, Keyword):
                if utilities.is_NormSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be normalized after the split method",
                        category=DataLeakageWarning,
                        stacklevel=2,
                    )
                elif utilities.is_StdSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be standardized after the split method",
                        category=DataLeakageWarning,
                        stacklevel=2,
                    )
                elif utilities.is_CatSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be encoded after the split method",
                        category=DataLeakageWarning,
                        stacklevel=2,
                    )
                elif utilities.is_FeatureSelected(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be Feature Selected after the split method",
                        category=DataLeakageWarning,
                        stacklevel=2,
                    )
                elif utilities.is_Scaled(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} @ column {stmt.pp.column} -> Data should be scaled after the split method",
                        category=DataLeakageWarning,
                        stacklevel=2,
                    )
                types += tuple({DatascienceTypeLattice.Status.SplittedTrainData})
                types += tuple({DatascienceTypeLattice.Status.SplittedTestData})
        state.result = {types}
        return state

    def strip_call_semantics(self, stmt: Call, state: State, interpreter: ForwardInterpreter) -> State:
        state.result = {DatascienceTypeLattice.Status.String}
        return state

    def slicing_access_semantics(self, stmt: Slicing, state, interpreter) -> State:
        """Semantics of a slicing access.

        :param stmt: slicing access statement to be executed
        :param state: state before executing the slicing access
        :return: state modified by the slicing access
        """
        target = self.semantics(stmt.target, state, interpreter).result
        lower = self.semantics(stmt.lower, state, interpreter).result if stmt.lower else {None}
        upper = self.semantics(stmt.upper, state, interpreter).result if stmt.upper else {None}
        stride = self.semantics(stmt.stride, state, interpreter).result if stmt.stride else {None}
        result = set()
        for primary, start, stop, step in itertools.product(target, lower, upper, stride):
            if hasattr(primary, "typ"):
                slicing = Slicing(primary.typ, primary, start, stop, step)
                result.add(slicing)
            else:
                top_type = TopLyraType
                slicing = Slicing(top_type, primary, start, stop, step)
                result.add(slicing)
        state.result = result
        return state

    def set_call_semantics(self, stmt: Call, state: State, interpreter: ForwardInterpreter) -> State:
        """Semantics of a call to 'set'.

        :param stmt: call to 'set' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            state.result = {SetDisplay(stmt.typ, list())}
            return state
        if len(stmt.arguments) == 1:
            argument = self.semantics(stmt.arguments[0], state, interpreter).result
            result = set()
            for expression in argument:
                if hasattr(expression, "typ"):
                    if isinstance(expression.typ, StringLyraType):
                        typ = SetLyraType(expression.typ)
                        result.add(CastOperation(typ, expression))
                    elif isinstance(expression.typ, ListLyraType):
                        typ = SetLyraType(expression.typ.typ)
                        result.add(CastOperation(typ, expression))
                    elif isinstance(expression.typ, TupleLyraType):
                        if all(typ == expression.typ.typs[0] for typ in expression.typ.typs):
                            typ = SetLyraType(expression.typ.typs[0])
                            result.add(CastOperation(typ, expression))
                        else:
                            error = f"Cast to list of {expression} is not yet implemented!"
                            raise NotImplementedError(error)
                    elif isinstance(expression.typ, SetLyraType):
                        result.add(expression)
                    elif isinstance(expression.typ, DictLyraType):
                        typ = SetLyraType(expression.typ.key_typ)
                        result.add(CastOperation(typ, expression))
                    else:
                        result.add(DatascienceTypeLattice.Status.Set)
                else:
                        result.add(DatascienceTypeLattice.Status.Set)
            state.result = result
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
