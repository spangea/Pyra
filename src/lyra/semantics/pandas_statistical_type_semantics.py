from lyra.core.expressions import (
    Subscription,
    Input,
)
from lyra.core.statements import (
    Call,
    SubscriptionAccess,
    Keyword,
    LiteralEvaluation,
    ListDisplayAccess,
    TupleDisplayAccess,
)
from lyra.core.types import (
    TopLyraType,
)
from lyra.engine.interpreter import Interpreter


from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice,
)

import lyra.semantics.utilities as utilities


class PandasStatisticalTypeSemantics:

    def DataFrame_call_semantics(
            stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def Series_call_semantics(
            stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def isna_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
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
            state.result = {
                StatisticalTypeLattice.Status.Top
            }
        return state

    def isna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def isnull_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        # isnull is an alias of isna
        return self.isna_library_call_semantics(stmt, state, interpreter)

    def isnull_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        # isnull is an alias of isna
        return self.isna_call_semantics(stmt, state, interpreter)

    def select_dtypes_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def set_flags_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def notnull_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
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
            state.result = {
                StatisticalTypeLattice.Status.Top
            }
        return state

    def notnull_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def notna_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.notnull_library_call_semantics(stmt, state, interpreter)

    def notna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.notnull_call_semantics(stmt, state, interpreter)

    def merge_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def sort_values_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def mode_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def value_counts_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def unique_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        # TODO
        pass

    def from_dict_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def memory_usage_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def drop_duplicates_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}  # inplace calls return None type
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def query_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def cumsum_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cumprod_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cummin_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def cummax_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def sample_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def where_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def rank_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def isin_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def rename_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def pct_change_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def crosstab_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def nlargest_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def nsmallest_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def explode_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def astype_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
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
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def add_suffix_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def corr_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        else:
            raise Exception("Unexpected type of caller")

    def get_dummies_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
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
            raise Exception("Unexpected type of caller")

    def bfill_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def compare_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
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
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        else:
            raise Exception("Unexpected type of caller")

    def droplevel_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def dropna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def duplicated_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.BoolSeries}
            return state
        else:
            raise Exception("Unexpected type of caller")

    def ffill_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def floordiv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def last_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def first_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        # DEPRECATED METHOD FOR SERIES AND DATAFRAME
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def kurtosis_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def mask_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def melt_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def nunique_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        else:
            raise Exception("Unexpected type of caller")

    def pivot_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def pow_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if (
            utilities.is_Series(state, caller)
            or utilities.is_DataFrame(state, caller)
            or utilities.is_Numeric(state, caller)
        ):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def prod_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_List(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
            return state
        elif utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
            return state
        else:
            raise Exception("Unexpected type of caller")

    def radd_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def rdiv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def rsub_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def rmul_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def rename_axis_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def reorder_levels_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def rfloordiv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def rtruediv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Series(state, caller) or utilities.is_DataFrame(state, caller):
            return self.return_same_type_as_caller(stmt, state, interpreter)
        else:
            raise Exception("Unexpected type of caller")

    def set_index_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def skew_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def sort_index_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def var_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_DataFrame(state, caller):
            state.result = {StatisticalTypeLattice.Status.Series}
        elif utilities.is_Series(state, caller):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        return state

    def loc_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        # We must arrive here from subscription_access_semantics
        if isinstance(stmt, SubscriptionAccess):
            call = Call(stmt.pp, stmt, [stmt.target.left, stmt.key], TopLyraType)
            caller = self.get_caller(call, state, interpreter)
            if utilities.is_DataFrame(state, caller):
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
            elif utilities.is_Series(state, caller):
                if isinstance(call.arguments[1], ListDisplayAccess):
                    state.result = {StatisticalTypeLattice.Status.Series}
                elif isinstance(call.arguments[1], LiteralEvaluation):
                    state.result = {StatisticalTypeLattice.Status.Scalar}
            return state
        else:
            raise Exception("Unexpected type of call")

    def iloc_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.loc_semantics(stmt, state, interpreter)

    def read_csv_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def DataFrame_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.DataFrame}
        return state

    def Series_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def drop_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
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
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def tail_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def describe_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def info_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return state

    def fillna_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        if utilities.is_inplace(stmt.arguments):
            self.semantics_without_inplace(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.NoneRet}
            return state
        return self.return_same_type_as_caller(stmt, state, interpreter)
