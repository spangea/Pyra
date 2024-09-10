from lyra.core.statements import Call

from lyra.engine.interpreter import Interpreter

from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice,
)
import lyra.semantics.utilities as utilities


class SklearnTypeSemantics:
    def MaxAbsScaler_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.MaxAbsScaler}
        return state

    def MinMaxScaler_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.MinMaxScaler}
        return state

    def StandardScaler_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.StandardScaler}
        return state

    def fit_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def transform_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Scaler(state, caller):
            if state.get_type(caller) in {
                StatisticalTypeLattice.Status.MinMaxScaler,
                StatisticalTypeLattice.Status.MaxAbsScaler,
            }:
                state.result = {StatisticalTypeLattice.Status.NormSeries}
            elif state.get_type(caller) == StatisticalTypeLattice.Status.StandardScaler:
                state.result = {StatisticalTypeLattice.Status.StdSeries}
        elif utilities.is_Encoder(state, caller):  # FIXME: to_array might me needed
            state.result = {StatisticalTypeLattice.Status.CatSeries}
        return state

    def fit_transform_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_Scaler(state, caller):
            if state.get_type(caller) in {
                StatisticalTypeLattice.Status.MinMaxScaler,
                StatisticalTypeLattice.Status.MaxAbsScaler,
            }:
                state.result = {StatisticalTypeLattice.Status.NormSeries}
            elif state.get_type(caller) == StatisticalTypeLattice.Status.StandardScaler:
                state.result = {StatisticalTypeLattice.Status.StdSeries}
        elif utilities.is_Encoder(state, caller):  # FIXME: to_array might me needed
            state.result = {StatisticalTypeLattice.Status.CatSeries}
        return state

    def inverse_transform_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        # FIXME: It could also be array [DataFrame]
        # The problem is that with Series it is called with the double subscription [[]]
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def OrdinalEncoder_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.OrdinalEncoder}
        return state

    def OneHotEncoder_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.OneHotEncoder}
        return state

    def LabelEncoder_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.LabelEncoder}
        return state

    def LabelBinarizer_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: Interpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.LabelBinarizer}
        return state
