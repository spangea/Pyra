from lyra.core.statements import Call

from lyra.engine.forward import ForwardInterpreter

from lyra.datascience.datascience_type_domain import (
    DatascienceTypeState,
    DatascienceTypeLattice
)

import lyra.semantics.utilities as utilities

class NumPyDatascienceTypeSemantics:

    def concatenate_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.Array}
        return state

    def unique_numpy_library_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        caller = self.get_caller(stmt, state, interpreter)

        if (utilities.is_NumericArray(state, caller) or utilities.is_NumericList(state, caller) or utilities.is_Numeric(
                state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            else:
                state.result = {DatascienceTypeLattice.Status.NumericArray}
        elif (utilities.is_StringArray(state, caller) or utilities.is_StringList(state, caller) or utilities.is_String(
                state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.StringArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(DatascienceTypeLattice.Status.StringArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.StringArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            else:
                state.result = {DatascienceTypeLattice.Status.StringArray}
        elif (utilities.is_BoolArray(state, caller) or utilities.is_BoolList(state, caller) or utilities.is_Boolean(
                state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.BoolArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(DatascienceTypeLattice.Status.BoolArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.BoolArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            else:
                state.result = {DatascienceTypeLattice.Status.BoolArray}
        elif (utilities.is_Array(state, caller) or utilities.is_List(state, caller)):
            if (utilities.has_to_return_index(stmt.arguments) and
                    utilities.has_to_return_inverse(stmt.arguments) and
                    utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.Array,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif ((utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_inverse(stmt.arguments))
                  or
                  (utilities.has_to_return_index(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))
                  or
                  (utilities.has_to_return_inverse(stmt.arguments) and
                   utilities.has_to_return_counts(stmt.arguments))):
                state.result = {(DatascienceTypeLattice.Status.Array,
                                 DatascienceTypeLattice.Status.NumericArray,
                                 DatascienceTypeLattice.Status.NumericArray)}
            elif (utilities.has_to_return_index(stmt.arguments) or
                  utilities.has_to_return_inverse(stmt.arguments) or
                  utilities.has_to_return_counts(stmt.arguments)):
                state.result = {(DatascienceTypeLattice.Status.Array,
                                 DatascienceTypeLattice.Status.NumericArray)}
            else:
                state.result = {DatascienceTypeLattice.Status.Array}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)
        return state

    def log_call_semantics(
            self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        if utilities.is_Array(state, stmt.arguments[0]) or utilities.is_List(state, stmt.arguments[0]):
            state.result = {DatascienceTypeLattice.Status.Array}
        elif utilities.is_Numeric(state, stmt.arguments[0]):
            state.result = {DatascienceTypeLattice.Status.Numeric}
        else:
            return self.relaxed_open_call_policy(stmt, state, interpreter)

        return state
