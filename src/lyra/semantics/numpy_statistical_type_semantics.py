from lyra.core.statements import Call

from lyra.engine.forward import ForwardInterpreter

from lyra.statistical.statistical_type_domain import (
    StatisticalTypeState,
    StatisticalTypeLattice
)

import lyra.semantics.utilities as utilities

class NumPyStatisticalTypeSemantics:

    def concatenate_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        state.result = {StatisticalTypeLattice.Status.Array}
        return state

    def log_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_Array(state, stmt.arguments[0]) or utilities.is_List(state, stmt.arguments[0]):
            state.result = {StatisticalTypeLattice.Status.Array}
        elif utilities.is_Numeric(state, stmt.arguments[0]):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        else:
            state.result = {StatisticalTypeLattice.Status.Top}

        return state
