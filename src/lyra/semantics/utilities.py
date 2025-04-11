from lyra.core.expressions import (
    Subscription,
    Literal,
    VariableIdentifier,
    ListDisplay,
    Input,
)
from lyra.core.statements import (
    Call,
    SubscriptionAccess,
    VariableAccess,
    Keyword,
    LiteralEvaluation,
    ListDisplayAccess,
)
from lyra.core.types import (
    DictLyraType, StringLyraType,
    ListLyraType,
    SetLyraType,
    DataFrameLyraType,
    IntegerLyraType,
    FloatLyraType,
    SeriesLyraType,
    BooleanLyraType,
)
from lyra.engine.forward import ForwardInterpreter

from lyra.datascience.datascience_type_domain import (
    DatascienceTypeState,
    DatascienceTypeLattice,
)
import copy
from lyra.core.types import TopLyraType

def is_PCA(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) == DatascienceTypeLattice.Status.PCA:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and \
        caller == DatascienceTypeLattice.Status.PCA:
        return True
    return False

def is_DataFrame(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame)):
                return True
        else:
            if isinstance(caller.typ, DataFrameLyraType):
                return True
    elif isinstance(caller, Subscription):
        if isinstance(caller.key, ListDisplay) and (
            isinstance(caller.target.typ, DataFrameLyraType)
            or (
                caller.target in state.store
                and state.get_type(caller.target)._less_equal(DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame))
            )
        ):
            return True
    elif isinstance(caller, Input) and isinstance(caller.typ, DataFrameLyraType):
        return True
    return False

def is_Series(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)
            ):
                return True
        else:
            if isinstance(caller.typ, SeriesLyraType):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller]._less_equal(
            DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)
        ):
            return True
        elif not isinstance(caller.key, ListDisplay) and (
            isinstance(caller.target.typ, DataFrameLyraType)
            or (
            caller.target in state.store
            and state.get_type(caller.target)
            == DatascienceTypeLattice.Status.DataFrame
            )
            or (
            hasattr(caller.target, 'variable')
            and caller.target.variable in state.store
            and state.get_type(caller.target.variable)
            == DatascienceTypeLattice.Status.DataFrame
            )
        ):
            return True
    elif isinstance(caller, Input) and isinstance(caller.typ, SeriesLyraType):
        return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and DatascienceTypeLattice(
        caller
    )._less_equal(DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)):
        return True
    return False


def is_StringSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] == (
                    DatascienceTypeLattice(DatascienceTypeLattice.Status.StringSeries)
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.StringSeries)
        ):
            return True
    elif (
            isinstance(caller, DatascienceTypeLattice.Status)
            and caller == DatascienceTypeLattice.Status.StringSeries
    ):
        return True
    return False


def is_RatioSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] == (
                DatascienceTypeLattice(DatascienceTypeLattice.Status.RatioSeries)
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller]._less_equal(
            DatascienceTypeLattice(DatascienceTypeLattice.Status.RatioSeries)
        ):
            return True
    elif (
        isinstance(caller, DatascienceTypeLattice.Status)
        and caller == DatascienceTypeLattice.Status.RatioSeries
    ):
        return True
    return False

def is_BoolSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] == (
                DatascienceTypeLattice(DatascienceTypeLattice.Status.BoolSeries)
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller]._less_equal(
            DatascienceTypeLattice(DatascienceTypeLattice.Status.BoolSeries)
        ):
            return True
    elif (
        isinstance(caller, DatascienceTypeLattice.Status)
        and caller == DatascienceTypeLattice.Status.BoolSeries
    ):
        return True
    return False

def is_CatSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] == DatascienceTypeLattice(
                DatascienceTypeLattice.Status.CatSeries
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller] == DatascienceTypeLattice(
            DatascienceTypeLattice.Status.CatSeries
        ):
            return True
    elif (
        isinstance(caller, DatascienceTypeLattice.Status)
        and caller == DatascienceTypeLattice.Status.CatSeries
    ):
        return True
    return False

def is_Tensor(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] == DatascienceTypeLattice(
                DatascienceTypeLattice.Status.Tensor
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if caller in state.store and state.store[caller] == DatascienceTypeLattice(
            DatascienceTypeLattice.Status.Tensor
        ):
            return True
    elif (
        isinstance(caller, DatascienceTypeLattice.Status)
        and caller == DatascienceTypeLattice.Status.Tensor
    ):
        return True
    return False

def is_SplittedData(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] in {
                DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTrainData),
                DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTestData),
            }:
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if caller in state.store and state.store[caller] in {
            DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTrainData),
            DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTestData),
        }:
            return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in {
        DatascienceTypeLattice.Status.SplittedTrainData,
        DatascienceTypeLattice.Status.SplittedTestData,
    }:
        return True
    return False

def is_SplittedTestData(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] in {
                DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTestData)
            }:
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if caller in state.store and state.store[caller] in {
            DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTestData)
        }:
            return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in {
        DatascienceTypeLattice.Status.SplittedTestData
    }:
        return True
    return False

def is_ExpSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] == DatascienceTypeLattice(
                DatascienceTypeLattice.Status.ExpSeries
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller] == DatascienceTypeLattice(
            DatascienceTypeLattice.Status.ExpSeries
        ):
            return True
    elif (
        isinstance(caller, DatascienceTypeLattice.Status)
        and caller == DatascienceTypeLattice.Status.ExpSeries
    ):
        return True
    return False

def is_NumericSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] == DatascienceTypeLattice(
                DatascienceTypeLattice.Status.NumericSeries
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller] == DatascienceTypeLattice(
            DatascienceTypeLattice.Status.NumericSeries
        ):
            return True
    elif (
        isinstance(caller, DatascienceTypeLattice.Status)
        and caller == DatascienceTypeLattice.Status.NumericSeries
    ):
        return True
    return False

def is_ScaledSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller] in {
                # DatascienceTypeLattice.Status.NormSeries,
                # DatascienceTypeLattice.Status.StdSeries,
                DatascienceTypeLattice(DatascienceTypeLattice.Status.NormSeries),
                DatascienceTypeLattice(DatascienceTypeLattice.Status.StdSeries),
            }:
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )

        if caller in state.store and state.store[caller] in {
            DatascienceTypeLattice(DatascienceTypeLattice.Status.NormSeries),
            DatascienceTypeLattice(DatascienceTypeLattice.Status.StdSeries),
        }:
            return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in {
        DatascienceTypeLattice.Status.NormSeries,
        DatascienceTypeLattice.Status.StdSeries,
    }:
        return True
    return False

def is_NormSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.NormSeries)
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )
        if caller in state.store and state.store[caller]._less_equal(
            DatascienceTypeLattice(DatascienceTypeLattice.Status.NormSeries)
        ):
            return True
    if state.get_type(caller) == {DatascienceTypeLattice.Status.NormSeries}:
        return True
    return False

def is_StdSeries(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.StdSeries)
            ):
                return True
    elif isinstance(caller, Subscription) or isinstance(caller, SubscriptionAccess):
        if isinstance(caller, SubscriptionAccess):
            if isinstance(caller.target, VariableAccess):
                tmp_target = caller.target.variable
                for v in state.variables:
                    if v.name == tmp_target.name:
                        tmp_target = v
            else:
                tmp_target = caller.target
            if isinstance(caller.key, LiteralEvaluation):
                tmp_key = caller.key.literal
            else:
                tmp_key = caller.key
            caller = Subscription(
                TopLyraType, tmp_target, tmp_key
            )
        if caller in state.store and state.store[caller]._less_equal(
            DatascienceTypeLattice(DatascienceTypeLattice.Status.StdSeries)
        ):
            return True
    if state.get_type(caller) == {DatascienceTypeLattice.Status.StdSeries}:
        return True
    return False

def is_Array(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.Array)
            ):
                return True
    return False

def is_NumericArray(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericArray)
            ):
                return True
    return False

def is_StringArray(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.StringArray)
            ):
                return True
    return False

def is_BoolArray(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.BoolArray)
            ):
                return True
    return False

def is_List(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.List)
            ):
                return True
        else:
            if isinstance(caller.typ, ListLyraType):
                return True
    if isinstance(caller, ListDisplay):
        return True
    return False

def is_NumericList(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericList)
            ):
                return True
    if isinstance(caller, ListDisplay):
        for x in caller.items:
            if not isinstance(x.typ, FloatLyraType) and not isinstance(x.typ, IntegerLyraType):
                return False
        return True
    if isinstance(caller, ListDisplayAccess):
        for x in caller.items:
            if not isinstance(x.typ, FloatLyraType) and not isinstance(x.typ, IntegerLyraType):
                return False
        return True
    return False

def is_StringList(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.StringList)
            ):
                return True
    if isinstance(caller, ListDisplay):
        for x in caller.items:
            if not isinstance(x.typ, StringLyraType):
                return False
        return True
    if isinstance(caller, ListDisplayAccess):
        for x in caller.items:
            if not isinstance(x.literal.typ, StringLyraType):
                return False
        return True
    return False

def is_BoolList(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.BoolList)
            ):
                return True
    if isinstance(caller, ListDisplay):
        for x in caller.items:
            if not isinstance(x.typ, BooleanLyraType):
                return False
        return True
    if isinstance(caller, ListDisplayAccess):
        for x in caller.items:
            if not isinstance(x.literal.typ, BooleanLyraType):
                return False
        return True
    return False

def is_Set(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.Set)
            ):
                return True
        else:
            if isinstance(caller.typ, SetLyraType):
                return True
    return False

def is_Dict(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.store[caller]._less_equal(
                DatascienceTypeLattice(DatascienceTypeLattice.Status.Dict)
            ):
                return True
        else:
            if isinstance(caller.typ, DictLyraType):
                return True
    return False


def is_String(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, StringLyraType):
        return True
    elif (
        isinstance(caller, VariableIdentifier)
        and state.get_type(caller) == DatascienceTypeLattice.Status.String
    ):
        return True
    elif isinstance(caller, Literal) and isinstance(caller.typ, StringLyraType):
        return True
    elif isinstance(caller, Input) and isinstance(caller.typ, StringLyraType):
        return True
    return False


def is_Numeric(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, IntegerLyraType) or isinstance(caller, FloatLyraType):
        return True
    elif (
        isinstance(caller, VariableIdentifier)
        and state.get_type(caller) == DatascienceTypeLattice.Status.Numeric
    ):
        return True
    elif isinstance(caller, Literal) and (
        isinstance(caller.typ, IntegerLyraType) or isinstance(caller.typ, FloatLyraType)
    ):
        return True
    elif isinstance(caller, Input) and (
        isinstance(caller.typ, IntegerLyraType) or isinstance(caller.typ, FloatLyraType)
    ):
        return True
    return False


def is_Boolean(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, BooleanLyraType):
        return True
    elif (
        isinstance(caller, VariableIdentifier)
        and state.get_type(caller) == DatascienceTypeLattice.Status.Boolean
    ):
        return True
    elif isinstance(caller, Literal) and (
        isinstance(caller.typ, BooleanLyraType)
    ):
        return True
    elif isinstance(caller, Input) and (
        isinstance(caller.typ, BooleanLyraType)
    ):
        return True
    return False


def is_Scaler(state, caller):
    scalerTypes = {
        DatascienceTypeLattice.Status.MinMaxScaler, DatascienceTypeLattice.Status.MaxAbsScaler,
        DatascienceTypeLattice.Status.StandardScaler, DatascienceTypeLattice.Status.FunctionTransformer,
        DatascienceTypeLattice.Status.KernelCenterer, DatascienceTypeLattice.Status.Normalizer,
        DatascienceTypeLattice.Status.PolynomialFeatures, DatascienceTypeLattice.Status.PowerTransformer,
        DatascienceTypeLattice.Status.QuantileTransformer, DatascienceTypeLattice.Status.RobustScaler,
        DatascienceTypeLattice.Status.SplineTransformer
    }
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) in scalerTypes:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in scalerTypes:
        return True
    return False


def is_Standardizer(state, caller):
    standardizerTypes = {
        DatascienceTypeLattice.Status.PowerTransformer,
        DatascienceTypeLattice.Status.RobustScaler,
        DatascienceTypeLattice.Status.StandardScaler,
        DatascienceTypeLattice.Status.QuantileTransformer,
        DatascienceTypeLattice.Status.KernelCenterer
    }
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) in standardizerTypes:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in standardizerTypes:
        return True
    return False


def is_Normalizer(state, caller):
    normalizerTypes = {
        DatascienceTypeLattice.Status.MaxAbsScaler,
        DatascienceTypeLattice.Status.MinMaxScaler,
        DatascienceTypeLattice.Status.Normalizer
    }
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) in normalizerTypes:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in normalizerTypes:
        return True
    return False


def is_Encoder(state, caller):
    encoderTypes = {
        DatascienceTypeLattice.Status.OrdinalEncoder, DatascienceTypeLattice.Status.OneHotEncoder,
        DatascienceTypeLattice.Status.LabelEncoder, DatascienceTypeLattice.Status.LabelBinarizer,
        DatascienceTypeLattice.Status.KBinsDiscretizer, DatascienceTypeLattice.Status.MultiLabelBinarizer,
        DatascienceTypeLattice.Status.TargetEncoder
    }
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) in encoderTypes:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in encoderTypes:
        return True
    return False

def is_FeatureSelected(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) in {
                DatascienceTypeLattice.Status.FeatureSelected
            }:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in {
        DatascienceTypeLattice.Status.FeatureSelected
    }:
        return True
    return False

def is_FeatureSelector(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) in {
                DatascienceTypeLattice.Status.FeatureSelector
            }:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in {
        DatascienceTypeLattice.Status.FeatureSelector
    }:
        return True
    return False

def is_Scaled(state, caller):
    if isinstance(caller, VariableAccess):
        caller = caller.variable
    if isinstance(caller, VariableIdentifier):
        if caller in state.store and not state.store[caller].is_top():
            if state.get_type(caller) in {
                DatascienceTypeLattice.Status.Scaled
            }:
                return True
    elif isinstance(caller, DatascienceTypeLattice.Status) and caller in {
        DatascienceTypeLattice.Status.Scaled
    }:
        return True
    return False

def is_Top(state, caller):
    if caller in state.store and state.store[caller].is_top():
        return True
    return False


def is_inplace(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "inplace" and arg.value:
            return True
    return False


def is_axis_eq_1(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "axis" and arg.value == 1:
            return True
    return False


def is_axis_eq_0(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "axis" and arg.value == 0:
            return True
    return False


def get_axis(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "axis":
            return arg.value
    return None


def remove_inplace(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "inplace" and arg.value:
            arguments.remove(arg)


def has_to_retstep(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "retstep" and arg.value:
            return True
    return False


def has_to_return_index(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "return_index" and arg.value:
            return True
    return False


def has_to_return_inverse(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "return_inverse" and arg.value:
            return True
    return False


def has_to_return_counts(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "return_counts" and arg.value:
            return True
    return False


def has_to_drop(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "drop" and arg.value:
            return True
    return False


def get_dtype(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "dtype" and arg.value:
            return arg.value
    return None

def is_dtype_numeric(arguments):
    numerictypes = {"np.float_", "np.float16", "np.float32", "np.float64",
                    "np.float128", "np.floating", "np.longfloat", "np.double",
                    "np.single", "float", "np.complex_", "np.complex64",
                    "np.complex128", "np.complex256", "np.csingle", "np.cfloat",
                    "np.clongfloat", "complex", "np.int_", "np.int8", "np.int16",
                    "np.int32", "np.int64", "np.intc", "np.intp", "np.longlong",
                    "np.short", "int", "np.uint", "np.unsignedinteger", "np.ubyte",
                    "np.uint8", "np.uint16", "np.uint32", "np.uint64", "np.uintc",
                    "np.uintp", "np.ulonglong", "np.ushort"}
    dtype = get_dtype(arguments)

    if dtype is not None and dtype in numerictypes:
        return True
    return False

def is_dtype_string(arguments) -> bool:
    stringtypes = {"np.string_", "np.str_", "np.bytes_", "np.character",
                   "np.unicode_", "str", "bytes", "memoryview"}
    dtype = get_dtype(arguments)

    if dtype is not None and dtype in stringtypes:
        return True
    return False

def is_dtype_bool(arguments) -> bool:
    booltypes = {"np.bool_", "bool"}
    dtype = get_dtype(arguments)

    if dtype is not None and dtype in booltypes:
        return True
    return False


def is_average_not_None(arguments):
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "average" and arg.value is None:
            return False
    return True


def is_zero_division_NaN(arguments):
    nans = {"np.nan", "np.NaN", "np.NAN"}
    for arg in arguments:
        if isinstance(arg, Keyword) and arg.name == "zero_division" and arg.value in nans:
            return True
    return False


class SelfUtilitiesSemantics:
    def get_caller(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ):
        tmp_state = copy.deepcopy(state)
        dfs = self.semantics(stmt.arguments[0], tmp_state, interpreter, get_caller=True).result
        assert len(dfs) == 1, (
            f"Function {stmt.name} is supposed to be called "
            "either on a single DataFrame or Series element"
        )
        caller = list(dfs)[0]
        return caller

    def semantics_without_inplace(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        remove_inplace(stmt.arguments)
        eval = self.semantics(stmt, state, interpreter)
        state._assign(caller, eval.result.pop())

    def forget_arg(self, caller, arg, state: DatascienceTypeState):
        if isinstance(arg, LiteralEvaluation):
            s = Subscription(TopLyraType, caller, arg.literal)
            if s in state.store:
                state.forget_variable(s)
            s = Subscription(TopLyraType, caller, arg.literal)
            if s in state.store:
                state.forget_variable(s)
        elif isinstance(arg, ListDisplayAccess):
            for i in arg.items:
                s = Subscription(TopLyraType, caller, i.literal)
                if s in state.store:
                    state.forget_variable(s)
        elif isinstance(arg, str):
            s = Subscription(TopLyraType, caller, Literal(StringLyraType(), arg))
            if s in state.store:
                state.forget_variable(s)

    def forget_columns(self, caller, stmt, state: DatascienceTypeState):
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "columns":
                if isinstance(arg.value, list):
                    for v in arg.value:
                        self.forget_arg(caller, v, state)
                else:
                    self.forget_arg(caller, arg.value, state)
            else:  # Directly a LiteralEvaluation or ListDisplayAccess
                self.forget_arg(caller, arg, state)

    def return_same_type_as_caller(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)
        if caller in state.store:
            # If datascience type info is already present, it is convenient to use it because it could be preciser
            datascience_type = state.get_type(caller)
            state.result = {datascience_type}
        else:
            if is_DataFrame(state, caller):
                state.result = {DatascienceTypeLattice.Status.DataFrame}
            elif is_Series(state, caller):
                # TODO: here we can be more precise if we return a datascience type element (not a Input/LyraType)
                state.result = {DatascienceTypeLattice.Status.Series}
            elif is_String(state, caller):
                state.result = {DatascienceTypeLattice.Status.String}
            elif is_Numeric(state, caller):
                state.result = {DatascienceTypeLattice.Status.Numeric}
            elif is_Set(state, caller):
                state.result = {DatascienceTypeLattice.Status.Set}
            elif is_Scaler(state, caller):
                state.result = state.get_type(caller)
            elif is_Encoder(state, caller):
                state.result = state.get_type(caller)
            else:
                return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state
