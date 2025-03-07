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


from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice,
)

import lyra.semantics.utilities as utilities


class SeabornStatisticalTypeSemantics:

    def set_seaborn_library_call_semantics(
        self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.NoneRet}
        return state
