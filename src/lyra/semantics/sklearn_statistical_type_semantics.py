from lyra.core.statements import Call, Keyword

from lyra.engine.forward import ForwardInterpreter

from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice,
)
import lyra.semantics.utilities as utilities

from lyra.core.expressions import (
    VariableIdentifier
)

from lyra.core.statements import (
    VariableAccess
)

from lyra.core.statistical_warnings import FixedNComponentsPCAWarning, PCAOnCategoricalWarning
import warnings

class SklearnTypeSemantics:
    def MaxAbsScaler_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.MaxAbsScaler}
        return state

    def MinMaxScaler_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.MinMaxScaler}
        return state

    def StandardScaler_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.StandardScaler}
        return state

    def fit_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_PCA(state, caller):
            self.issue_pca_warnings(stmt, state, interpreter)
        return self.return_same_type_as_caller(stmt, state, interpreter)

    def issue_pca_warnings(self, stmt, state, interpreter):
        warning_raised = False
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_PCA(state, caller) and state.get_type(caller) == StatisticalTypeLattice.Status.PCA:
            arg = stmt.arguments[1]
            if utilities.is_DataFrame(state, arg) and isinstance(arg, VariableAccess) and arg.variable in state.variables:
                for e in state.variables:
                    if e == arg.variable and e in state.subscriptions:
                        for sub in state.subscriptions[e]:
                            if sub in state.store and state.get_type(sub) == StatisticalTypeLattice.Status.CatSeries:
                                warnings.warn(
                                    f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> PCA is applied to Dataframe containing a categorical Series, it is better to use MixedPCA.",
                                    category=PCAOnCategoricalWarning,
                                    stacklevel=2,
                                )
                                warning_raised = True
                                break
                if not warning_raised and interpreter.warning_level == "possible":
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> PCA might be applied to Dataframe containing a categorical Series, it is better to use MixedPCA.",
                        category=PCAOnCategoricalWarning,
                        stacklevel=2,
                    )

    def transform_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
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
        elif utilities.is_PCA(state, caller):
            self.issue_pca_warnings(stmt, state, interpreter)
        return state

    def fit_transform_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
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
        elif utilities.is_PCA(state, caller):
            self.issue_pca_warnings(stmt, state, interpreter)
        return state

    def inverse_transform_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        # FIXME: It could also be array [DataFrame]
        # The problem is that with Series it is called with the double subscription [[]]
        state.result = {StatisticalTypeLattice.Status.Series}
        return state

    def OrdinalEncoder_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.OrdinalEncoder}
        return state

    def OneHotEncoder_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.OneHotEncoder}
        return state

    def LabelEncoder_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.LabelEncoder}
        return state

    def LabelBinarizer_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.LabelBinarizer}
        return state

    def PCA_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        args = stmt.arguments
        for a in args:
            if isinstance(a, Keyword) and a.name == "n_components":
                if type(a.value) in (int, float):   # Constant number
                    warnings.warn(
                        f"Warning [definite]: in {stmt} @ line {stmt.pp.line} -> n_components is {a.value}, this might be a wrong assumption. It may be better to run multiple experiments.",
                        category=FixedNComponentsPCAWarning,
                        stacklevel=2,
                    )
                elif interpreter.warning_level == "possible":
                    warnings.warn(
                        f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> n_components might be a wrong assumption. It may be better to run multiple experiments.",
                        category=FixedNComponentsPCAWarning,
                        stacklevel=2,
                    )
        state.result = {StatisticalTypeLattice.Status.PCA}
        return state
