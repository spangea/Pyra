from lyra.core.expressions import (
    Subscription, VariableIdentifier,
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


class SeabornDatascienceTypeSemantics:

    def set_seaborn_library_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state
