from lyra.core.expressions import (
    Subscription,
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
from lyra.engine.forward import ForwardInterpreter


from lyra.datascience.datascience_type_domain import (
    DatascienceTypeState,
    DatascienceTypeLattice,
)

import lyra.semantics.utilities as utilities

class TorchDatascienceTypeSemantics:
    def empty_cache_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def save_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def tensor_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state

    def zeros_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state

    def ones_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state

    def empty_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state

    def absolute_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state

    def acos_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state

    def arccos_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.acos_call_semantics(stmt, state, interpreter)

    def acosh_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state

    def arccosh_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        return self.acosh_call_semantics(stmt, state, interpreter)

    def backward_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def clip_grad_norm__call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Tensor}
        return state



