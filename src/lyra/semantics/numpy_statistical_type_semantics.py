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

    def unique_numpy_library_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if (utilities.is_NumericArray(state, caller) or utilities.is_NumericList(state, caller) or utilities.is_Numeric(
                state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            else:
                state.result = {StatisticalTypeLattice.Status.NumericArray}
        elif (utilities.is_StringArray(state, caller) or utilities.is_StringList(state, caller) or utilities.is_String(
                state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.StringArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(StatisticalTypeLattice.Status.StringArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.StringArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            else:
                state.result = {StatisticalTypeLattice.Status.StringArray}
        elif (utilities.is_BoolArray(state, caller) or utilities.is_BoolList(state, caller) or utilities.is_Boolean(
                state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.BoolArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(StatisticalTypeLattice.Status.BoolArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.BoolArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            else:
                state.result = {StatisticalTypeLattice.Status.BoolArray}
        elif (utilities.is_Array(state, caller) or utilities.is_List(state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.Array,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(StatisticalTypeLattice.Status.Array,
                                 StatisticalTypeLattice.Status.NumericArray,
                                 StatisticalTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(StatisticalTypeLattice.Status.Array,
                                 StatisticalTypeLattice.Status.NumericArray)}
            else:
                state.result = {StatisticalTypeLattice.Status.Array}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def log_call_semantics(
            self, stmt: Call, state: StatisticalTypeState, interpreter: ForwardInterpreter
    ) -> StatisticalTypeState:
        if utilities.is_Array(state, stmt.arguments[0]) or utilities.is_List(state, stmt.arguments[0]):
            state.result = {StatisticalTypeLattice.Status.Array}
        elif utilities.is_Numeric(state, stmt.arguments[0]):
            state.result = {StatisticalTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

        return state
