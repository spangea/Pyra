import os
import shutil
import zipfile
import pandas as pd
from pathlib import Path
import lyra.config as config
import warnings

from lyra.core.datascience_warnings import (
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


from lyra.datascience.datascience_type_domain import (
    DatascienceTypeState,
    DatascienceTypeLattice,
)

import lyra.semantics.utilities as utilities


class PandasDatascienceTypeSemantics:

    def DataFrame_call_semantics(
            stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.DataFrame}
        return state

    def Series_call_semantics(
            stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Series}
        return state

    def isna_library_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.DataFrame}
        elif utilities.is_Array(state, caller):
            state.result = {DatascienceTypeLattice.Status.BoolArray}
        elif utilities.is_Numeric(state, caller) or utilities.is_String(state, caller):
            state.result = {DatascienceTypeLattice.Status.Boolean}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def isna_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def isnull_library_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # isnull is an alias of isna
        return self.isna_library_call_semantics(stmt, state, interpreter)

    def isnull_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # isnull is an alias of isna
        return self.isna_call_semantics(stmt, state, interpreter)

    def select_dtypes_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.DataFrame}
        return state

    def set_flags_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def notnull_library_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.DataFrame}
        elif utilities.is_Array(state, caller):
            state.result = {DatascienceTypeLattice.Status.BoolArray}
        elif utilities.is_Numeric(state, caller) or utilities.is_String(state, caller):
            state.result = {DatascienceTypeLattice.Status.Boolean}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def notnull_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def notna_library_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.notnull_library_call_semantics(stmt, state, interpreter)

    def notna_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.notnull_call_semantics(stmt, state, interpreter)

    def merge_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.DataFrame}
        return state

    def sort_values_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def mode_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def value_counts_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Series}
        return state

    def unique_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if utilities.is_StringSeries(state, caller) or utilities.is_CatSeries(state, caller):
            state.result = {DatascienceTypeLattice.Status.StringArray}
        elif utilities.is_BoolSeries(state, caller):
            state.result = {DatascienceTypeLattice.Status.BoolArray}
        elif (utilities.is_RatioSeries(state, caller) or
              utilities.is_ScaledSeries(state, caller) or
              utilities.is_NumericSeries(state, caller) or
              utilities.is_ExpSeries(state, caller)):
            state.result = {DatascienceTypeLattice.Status.NumericArray}
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Array}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def from_dict_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.DataFrame}
        return state

    def memory_usage_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        elif utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def drop_duplicates_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}  # inplace calls return None type
            # Directly change has_duplicates property of the caller to NO
            subset = None
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "subset":
                    subset = arg.value
                    break
            caller = self.get_caller(stmt, state, interpreter)
            if utilities.is_DataFrame(state, caller):
                if isinstance(caller, VariableAccess):
                    caller = caller.variable
                if caller in state.variables:
                    for e in state.variables:
                        if e == caller:
                            tmp = e
                            state.variables.remove(e)
                            tmp.has_duplicates = Status.NO
                            state.variables.add(tmp)
                            break
            return state
        subset = None
        for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "subset":
                    subset = arg.value
                    break
        if subset is None:  # Drop duplicates on all columns
            caller = self.get_caller(stmt, state, interpreter)
            if utilities.is_DataFrame(state, caller):
                if isinstance(caller, VariableAccess):
                    caller = caller.variable
                if caller in state.variables:
                    # Create a copy of the caller to represent the new DataFrame
                    new_var = VariableIdentifier(caller.typ, f"{caller}_lyracopy")
                    state.variables.add(new_var)
                    for e in state.variables:
                        if e == new_var:
                            tmp = e
                            tmp.has_duplicates = Status.NO
                            break
                    tmp_state = self.return_same_type_as_caller(stmt, state, interpreter)
                    tmp_result = tmp_state.result.pop()
                    state.result = {(tmp_result, new_var)}
                    return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def query_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        state.result = {DatascienceTypeLattice.Status.DataFrame}
        return state

    def cumsum_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cumprod_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cummin_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cummax_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def sample_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        is_reproducible = False
        # Keyword case for random_state
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "random_state":
                is_reproducible = True
                break
        # Positional case for random_state - More than 5 arguments and the first five are positional
        if not is_reproducible and len(stmt.arguments) > 5:
            is_reproducible = True
            for arg in stmt.arguments[1:6]:
                if isinstance(arg, Keyword):
                    is_reproducible = False
                    break   # After the first keyword argument, all the following must be keyword arguments
        if not is_reproducible:
            warnings.warn(
                f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} the random state is not set, the experiment might not be reproducible.",
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
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def rank_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def isin_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def rename_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def pct_change_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def crosstab_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.DataFrame}
        return state

    def nlargest_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def nsmallest_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def explode_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def astype_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            for arg in stmt.arguments:
                if isinstance(arg, LiteralEvaluation) and arg.literal.val == "category":
                    state.result = {DatascienceTypeLattice.Status.CatSeries}
                    return state
                if isinstance(arg, LiteralEvaluation) and arg.literal.val == "string":
                    state.result = {DatascienceTypeLattice.Status.StringSeries}
                    return state
        elif utilities.is_DataFrame(state, caller):
            # TODO: handle scenarios like df.astype({'col1': 'int32'})
            # which only changes the type of col1
            pass
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def add_prefix_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def add_suffix_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def corr_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def get_dummies_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # FIXME: Should handle CategoricalSeries somehow
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and arg.name == "columns":
                    for a in arg.value:
                        if isinstance(a, str):
                            sub = Subscription(TopLyraType, caller, '"' + a + '"')
                        else:
                            sub = Subscription(TopLyraType, caller, a.id)
                        state._assign(sub, DatascienceTypeLattice.Status.CatSeries)
            state.result = {DatascienceTypeLattice.Status.DataFrame}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def bfill_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def compare_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "x":
                if arg.value == 0 or arg.value == "index":
                    state.result = {DatascienceTypeLattice.Status.Series}
                elif arg.value == 1 or arg.value == "columns":
                    state.result = {DatascienceTypeLattice.Status.DataFrame}
                return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cov_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def droplevel_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def dropna_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            subset = None
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and (arg.name == "subset" or arg.name == "thresh"):
                    subset = arg.value
                    break
            if subset is None:
                caller = self.get_caller(stmt, state, interpreter)
                if utilities.is_DataFrame(state, caller):
                    if isinstance(caller, VariableAccess):
                        caller = caller.variable
                    if caller in state.variables:
                        for e in state.variables:
                            if e == caller:
                                tmp = e
                                state.variables.remove(e)
                                tmp.has_na_values = Status.NO
                                state.variables.add(tmp)
                                break
                return state
        subset = None
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and (arg.name == "subset" or arg.name == "thresh"):
                subset = arg.value
                break
        if subset is None:
            caller = self.get_caller(stmt, state, interpreter)
            if utilities.is_DataFrame(state, caller):
                if isinstance(caller, VariableAccess):
                    caller = caller.variable
                if caller in state.variables:
                    # Create a copy of the caller to represent the new DataFrame
                    new_var = VariableIdentifier(caller.typ, f"{caller}_lyracopy")
                    state.variables.add(new_var)
                    for e in state.variables:
                        if e == new_var:
                            tmp = e
                            tmp.has_na_values = Status.NO
                            break
                    tmp_state = self.return_same_type_as_caller(stmt, state, interpreter)
                    tmp_result = tmp_state.result.pop()
                    state.result = {(tmp_result, new_var)}
                    return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def duplicated_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.BoolSeries}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def ffill_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def floordiv_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def last_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def first_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def kurtosis_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        return state

    def mask_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def melt_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def nunique_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def pivot_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def pow_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
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

    def radd_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rdiv_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rsub_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rmul_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rename_axis_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def reorder_levels_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rfloordiv_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def rtruediv_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def set_index_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def skew_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def sort_index_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def var_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {DatascienceTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def loc_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        # We must arrive here from subscription_access_semantics
        if isinstance(stmt, SubscriptionAccess):
            call = Call(stmt.pp, stmt, [stmt.target, stmt.key], TopLyraType)
            accessed_var = stmt.target.target.variable
            if utilities.is_DataFrame(state, accessed_var):
                if isinstance(call.arguments[1], ListDisplayAccess):
                    state.result = {DatascienceTypeLattice.Status.DataFrame}
                elif isinstance(call.arguments[1], LiteralEvaluation):
                    state.result = {DatascienceTypeLattice.Status.Series}
                elif isinstance(call.arguments[1], TupleDisplayAccess):
                    if len(call.arguments[1].items) == 1:
                        state.result = {
                            DatascienceTypeLattice.Status.DataFrame
                        }
                    else:
                        state.result = {DatascienceTypeLattice.Status.Scalar}
            elif utilities.is_Series(state, accessed_var):
                if isinstance(call.arguments[1], ListDisplayAccess):
                    state.result = {DatascienceTypeLattice.Status.Series}
                elif isinstance(call.arguments[1], LiteralEvaluation):
                    state.result = {DatascienceTypeLattice.Status.Scalar}
            return state
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

    def iloc_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.loc_semantics(stmt, state, interpreter)

    def read_csv_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        last_folder_in_name = None
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
            benchmark_dir = "/Users/greta/PhD/kaggle/input" # TODO: Do not use hardcoded paths
            last_folder_in_name = fun_args[0].split("/")[-2] + ".zip"
            # Check if there is a zip file in the benchmark directory with the same name as the directory from which the file is read
            if last_folder_in_name in os.listdir(benchmark_dir):
                # Unzip the file in a temporary directory
                with zipfile.ZipFile(os.path.join(benchmark_dir, last_folder_in_name), 'r') as zip_ref:
                    last_folder_in_name = last_folder_in_name.replace(".zip", "")
                    zip_ref.extractall(os.path.join("/tmp", last_folder_in_name))
                    tmp_name = os.path.join("/tmp", last_folder_in_name, fun_args[0].split("/")[-1])
                    concrete_df = pd.read_csv(tmp_name, **fun_kwargs)
                    shutil.rmtree(os.path.join("/tmp", last_folder_in_name))
            else:
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
            has_na_values = concrete_df.isna().values.any()
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
            state.result = {(DatascienceTypeLattice.Status.DataFrame, frozenset(dtype_info.items()), is_high_dim, has_duplicates, has_na_values, is_small, frozenset(sorting_info.items()))}
        except Exception as e:
            print("It was not possible to read the concrete DataFrame due to error: ", e)
            state.result = {DatascienceTypeLattice.Status.DataFrame}
            if last_folder_in_name is not None and last_folder_in_name in os.listdir("/tmp"):
                shutil.rmtree(os.path.join("/tmp", last_folder_in_name))
        return state

    def DataFrame_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.DataFrame}
        return state

    def Series_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Series}
        return state

    def drop_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_inplace(stmt.arguments):
            if utilities.is_axis_eq_1(stmt.arguments):
                self.forget_columns(caller, stmt, state)
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def head_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def tail_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def describe_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def info_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return state

    def fillna_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {DatascienceTypeLattice.Status.NoneRet}
            subset = None
            for arg in stmt.arguments:
                if isinstance(arg, Keyword) and (arg.name == "limit" or arg.name == "axis"):
                    subset = arg.value
                    break
            if subset is None:
                caller = self.get_caller(stmt, state, interpreter)
                if utilities.is_DataFrame(state, caller):
                    if isinstance(caller, VariableAccess):
                        caller = caller.variable
                    if caller in state.variables:
                        for e in state.variables:
                            if e == caller:
                                tmp = e
                                state.variables.remove(e)
                                tmp.has_na_values = Status.NO
                                state.variables.add(tmp)
                                break
            return state
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller) and isinstance(caller, VariableIdentifier):
            caller_to_print = caller if not isinstance(caller, DatascienceTypeLattice.Status) else stmt
            if caller in state.variables:
                for item in state.variables:
                    if item == caller:
                        caller = item
                        break
            if interpreter.warning_level == "potential":
                if caller.is_small == Status.NO:
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} has many instances, but handling missing values with fillna might change the distribution.",
                        category=InappropriateMissingValuesWarning,
                        stacklevel=2,
                    )
                else:
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {caller_to_print} may have few instances, handling missing values with fillna might change the distribution.",
                        category=InappropriateMissingValuesWarning,
                        stacklevel=2,
                    )
        subset = None
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and (arg.name == "limit" or arg.name == "axis"):
                subset = arg.value
                break
        if subset is None:
            caller = self.get_caller(stmt, state, interpreter)
            if utilities.is_DataFrame(state, caller):
                if isinstance(caller, VariableAccess):
                    caller = caller.variable
                if caller in state.variables:
                    # Create a copy of the caller to represent the new DataFrame
                    new_var = VariableIdentifier(caller.typ, f"{caller}_lyracopy")
                    state.variables.add(new_var)
                    for e in state.variables:
                        if e == new_var:
                            tmp = e
                            tmp.has_na_values = Status.NO
                            break
                    tmp_state = self.return_same_type_as_caller(stmt, state, interpreter)
                    tmp_result = tmp_state.result.pop()
                    state.result = {(tmp_result, new_var)}
                    return state
        return self.return_same_type_as_caller(stmt, state, interpreter)
