from lyra.engine.forward import ForwardInterpreter

from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice,
)
import lyra.semantics.utilities as utilities

from lyra.core.statements import (
    Keyword,
    Call,
    VariableAccess
)
from lyra.semantics.utilities import SelfUtilitiesSemantics

from lyra.core.statistical_warnings import (
    DataLeakage
)

import warnings

from lyra.core.expressions import (
    VariableIdentifier
)

from lyra.core.statistical_warnings import FixedNComponentsPCAWarning, PCAOnCategoricalWarning

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
        data = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_SplittedTestData(state, data):
            warnings.warn(
                f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> The fit method should be used on train data only.",
                category=DataLeakage,
                stacklevel=2,
            )
        elif utilities.is_PCA(state, caller):
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
            if utilities.is_Normalizer(state, caller):
                state.result = {StatisticalTypeLattice.Status.NormSeries}
            elif utilities.is_Standardizer(state, caller):
                state.result = {StatisticalTypeLattice.Status.StdSeries}
            else:
                state.result = {StatisticalTypeLattice.Status.Scaled}
        elif utilities.is_Encoder(state, caller):  # FIXME: to_array might me needed
            state.result = {StatisticalTypeLattice.Status.CatSeries}
        elif utilities.is_FeatureSelector(state, caller):
            state.result = {StatisticalTypeLattice.Status.FeatureSelected}
        elif utilities.is_PCA(state, caller):
            self.issue_pca_warnings(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.DataFrameFromPCA}
        else:
            state.result = {StatisticalTypeLattice.Status.Top}
        return state

    def fit_transform_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        data = list(self.semantics(stmt.arguments[1], state, interpreter).result)[0]
        caller = self.get_caller(stmt, state, interpreter)
        if utilities.is_SplittedTestData(state, data):
            warnings.warn(
                f"Warning [possible]: in {stmt} @ line {stmt.pp.line} -> The fit_transform method should be used on train data only.",
                category=DataLeakage,
                stacklevel=2,
            )
        elif utilities.is_PCA(state, caller):
            self.issue_pca_warnings(stmt, state, interpreter)
            state.result = {StatisticalTypeLattice.Status.DataFrameFromPCA}
            return state
        return self.transform_call_semantics(stmt, state, interpreter)

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

    def Binarizer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Binarizer}
        return state

    def FunctionTransformer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FunctionTransformer}
        return state

    def KBinsDiscretizer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.KBinsDiscretizer}
        return state

    def KernelCenterer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.KernelCenterer}
        return state

    def MultiLabelBinarizer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.MultiLabelBinarizer}
        return state

    def Normalizer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Normalizer}
        return state

    def PolynomialFeatures_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.PolynomialFeatures}
        return state

    def PowerTransformer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.PowerTransformer}
        return state

    def QuantileTransformer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.QuantileTransformer}
        return state

    def RobustScaler_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.RobustScaler}
        return state

    def SplineTransformer_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.SplineTransformer}
        return state

    def TargetEncoder_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.TargetEncoder}
        return state

    def GenericUnivariateSelect_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def RFE_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def RFECV_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SelectFdr_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SelectFpr_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SelectFromModel_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SelectFwe_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SelectKBest_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SelectPercentile_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SelectorMixin_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def SequentialFeatureSelector_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
        return state

    def VarianceThreshold_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.FeatureSelector}
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
