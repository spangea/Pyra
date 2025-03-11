import os
import pandas as pd
from pathlib import Path
import lyra.config as config
import warnings

from lyra.core.statistical_warnings import (
    InappropriateMissingValuesWarning,
    ReproducibilityWarning
)
from lyra.core.expressions import (
    Subscription,
    VariableIdentifier, Status
)
from lyra.core.statements import (
    Call,
    SubscriptionAccess,
    Keyword,
    LiteralEvaluation,
    ListDisplayAccess,
    TupleDisplayAccess,
    VariableAccess
)
from lyra.core.types import (
    TopLyraType,
)
from lyra.engine.forward import ForwardInterpreter


from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice,
)

import lyra.semantics.utilities as utilities


class PandasStatisticalTypeSemantics:

    def DataFrame_call_semantics(
            stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def Series_call_semantics(
            stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def isna_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.DataFrame}
        elif utilities.is_Array(state, caller):
            state.result = {StatisticalTypeLattice.Status.BoolArray}
        elif utilities.is_Numeric(state, caller) or utilities.is_String(state, caller):
            state.result = {StatisticalTypeLattice.Status.Boolean}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def isna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def isnull_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # isnull is an alias of isna
        return self.isna_library_call_semantics(stmt, state, interpreter)

    def isnull_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # isnull is an alias of isna
        return self.isna_call_semantics(stmt, state, interpreter)

    def select_dtypes_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def set_flags_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def notnull_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.DataFrame}
        elif utilities.is_Array(state, caller):
            state.result = {StatisticalTypeLattice.Status.BoolArray}
        elif utilities.is_Numeric(state, caller) or utilities.is_String(state, caller):
            state.result = {StatisticalTypeLattice.Status.Boolean}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def notnull_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def notna_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.notnull_library_call_semantics(stmt, state, interpreter)

    def notna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.notnull_call_semantics(stmt, state, interpreter)

    def merge_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def sort_values_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def mode_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def value_counts_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def unique_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_StringSeries(state, caller) or utilities.is_CatSeries(state, caller):
            state.result = {StatisticalTypeLattice.Status.StringArray}
        elif utilities.is_BoolSeries(state, caller):
            state.result = {StatisticalTypeLattice.Status.BoolArray}
        elif (utilities.is_RatioSeries(state, caller) or
              utilities.is_ScaledSeries(state, caller) or
              utilities.is_NumericSeries(state, caller) or
              utilities.is_ExpSeries(state, caller)):
            state.result = {StatisticalTypeLattice.Status.NumericArray}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Array}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def from_dict_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def memory_usage_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def drop_duplicates_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        subset = None
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "subset":
                subset = arg.value
                break
        if subset is None:      # Drop duplicates on all columns
            caller = self.get_caller(stmt, state, interpreter)
            if utilities.is_DataFrame(state, caller):
                if isinstance(caller, VariableAccess):
                    caller = caller.variable
                if caller in state.variables:
                    for e in state.variables:
                        if e == caller and e.has_duplicates == Status.YES:
                            tmp = e
                            state.variables.remove(e)
                            tmp.has_duplicates = Status.NO
                            state.variables.add(tmp)
                            break
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}  # inplace calls return None type
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def query_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def cumsum_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cumprod_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cummin_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cummax_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def sample_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        is_reproducible = False
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "random_state":
                is_reproducible = True
                break
        if not is_reproducible:
            warnings.warn(
                f"Warning [definite]: in {stmt} @ line {stmt.pp.line} the random state is not set, the experiment might not be reproducible.",
                category=ReproducibilityWarning,
                stacklevel=2,
            )
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            if isinstance(caller, VariableAccess):
                caller = caller.variable
            if caller in state.variables:
                for e in state.variables:
                    if e == caller:
                        tmp = e
                        state.variables.remove(e)
                        tmp.is_shuffled = Status.YES
                        state.variables.add(tmp)
                        break
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def where_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def rank_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def isin_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def rename_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def pct_change_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def crosstab_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def nlargest_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def nsmallest_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def explode_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def astype_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            for arg in stmt.arguments:
                if isinstance(arg, LiteralEvaluation) and arg.literal.val == "category":
                    state.result = {StatisticalTypeLattice.Status.CatSeries}
                    return state
                if isinstance(arg, LiteralEvaluation) and arg.literal.val == "string":
                    state.result = {StatisticalTypeLattice.Status.StringSeries}
                    return state
        elif utilities.is_DataFrame(state, caller):
            # TODO: handle scenarios like df.astype({'col1': 'int32'})
            # which only changes the type of col1
            pass
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def add_prefix_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def add_suffix_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def corr_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def get_dummies_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # FIXME: Should handle CategoricalSeries somehow
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "columns":
                    for a in arg.value:
                        if isinstance(a, str):
                            sub = Subscription(None, caller, '"' + a + '"')
                        else:
                            sub = Subscription(None, caller, a.id)
                        state._assign(sub, StatisticalTypeLattice.Status.CatSeries)
            state.result = {StatisticalTypeLattice.Status.DataFrame}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def bfill_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def compare_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "x":
                if arg.value == 0 or arg.value == "index":
                    state.result = {StatisticalTypeLattice.Status.Series}
                elif arg.value == 1 or arg.value == "columns":
                    state.result = {StatisticalTypeLattice.Status.DataFrame}
                return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cov_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def droplevel_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def dropna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def duplicated_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.BoolSeries}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def ffill_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def floordiv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def last_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def first_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def kurtosis_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def mask_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def melt_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def nunique_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def pivot_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def pow_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if (
            utilities.is_Series(state, caller)
            or utilities.is_DataFrame(state, caller)
            or utilities.is_Numeric(state, caller)
            or utilities.is_Tensor(state, caller)
        ):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def prod_call_semantics(
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

    def radd_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rdiv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rsub_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rmul_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rename_axis_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def reorder_levels_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rfloordiv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rtruediv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def set_index_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def skew_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def sort_index_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def var_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def loc_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # We must arrive here from subscription_access_semantics
        if isinstance(stmt, SubscriptionAccess):
            call = Call(stmt.pp, stmt, [stmt.target, stmt.key], TopLyraType)
            accessed_var = stmt.target.target.variable
            if utilities.is_DataFrame(state, accessed_var):
                if isinstance(call.arguments[1], ListDisplayAccess):
                    state.result = {StatisticalTypeLattice.Status.DataFrame}
                elif isinstance(call.arguments[1], LiteralEvaluation):
                    state.result = {StatisticalTypeLattice.Status.Series}
                elif isinstance(call.arguments[1], TupleDisplayAccess):
                    if len(call.arguments[1].items) == 1:
                        state.result = {
                            StatisticalTypeLattice.Status.DataFrame
                        }
                    else:
                        state.result = {StatisticalTypeLattice.Status.Scalar}
            elif utilities.is_Series(state, accessed_var):
                if isinstance(call.arguments[1], ListDisplayAccess):
                    state.result = {StatisticalTypeLattice.Status.Series}
                elif isinstance(call.arguments[1], LiteralEvaluation):
                    state.result = {StatisticalTypeLattice.Status.Scalar}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def iloc_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.loc_semantics(stmt, state, interpreter)

    def read_csv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        try:
            dir = Path(config.args.python_file).parent
            fun_args = []
            fun_kwargs = {}
            for a in stmt.arguments:
                if hasattr(a, "literal"):
                    fun_args.append(a.literal.val)
                elif "=" in str(a):
                    key, value = str(a).split("=")
                    fun_kwargs[key] = value
                else:
                    raise Exception("Unexpected argument type")
            fun_args[0] = os.path.join(dir, fun_args[0])
            concrete_df = pd.read_csv(fun_args[0], **fun_kwargs)
            shape = concrete_df.shape
            # The concrete dataframe is high dimensional if the number of columns is similar to the number of rows
            # e.g. they are not the dobule of each other
            if shape[0] < 2 * shape[1]:
                is_high_dim = True
            else:
                is_high_dim = False
            if len(concrete_df) <= 100:
                is_small = True
            else:
                is_small = False
            has_duplicates = concrete_df.duplicated().any()
            dtype_info = {}
            for col in concrete_df.columns:
                dtype_info[col] = concrete_df[col].dtype
            # For each Series check if it is increasing or decreasing
            sorting_info = {}
            for col in concrete_df.columns:
                if concrete_df[col].is_monotonic_increasing and concrete_df[col].is_monotonic_decreasing:
                    sorting_info[col] = "constant"
                elif concrete_df[col].is_monotonic_increasing:
                    sorting_info[col] = "increasing"
                elif concrete_df[col].is_monotonic_decreasing:
                    sorting_info[col] = "decreasing"
                else:
                    sorting_info[col] = "not_sorted"
            state.result = {(StatisticalTypeLattice.Status.DataFrame, frozenset(dtype_info.items()), is_high_dim, has_duplicates, is_small, frozenset(sorting_info.items()))}
        except Exception as e:
            print("It was not possible to read the concrete DataFrame due to error: ", e)
            state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def DataFrame_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def Series_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def drop_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_inplace(stmt.arguments):
            if utilities.is_axis_eq_1(stmt.arguments):
                self.forget_columns(caller, stmt, state)
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def head_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def tail_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def describe_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def info_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        return state

    def fillna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller) and isinstance(caller, VariableIdentifier):
            caller_to_print = caller if not isinstance(caller, StatisticalTypeLattice.Status) else stmt
            if caller in state.variables:
                caller = next((x for x in state.variables if x == caller))
            if caller.is_small == Status.NO:
                warnings.warn(
                    f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} has many instances, therefore handling missing values with fillna might change the distribution.",
                    category=InappropriateMissingValuesWarning,
                    stacklevel=2,
                )
            else:
                warnings.warn(
                    f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} may have few instances, but handling missing values with fillna might change the distribution.",
                    category=InappropriateMissingValuesWarning,
                    stacklevel=2,
                )
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)
