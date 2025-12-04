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
    VariableAccess,
)
from lyra.core.types import (
    TopLyraType,
)
from lyra.engine.forward import ForwardInterpreter


from lyra.datascience.datascience_type_domain import (
    DatascienceTypeState,
    DatascienceTypeLattice,
)

from lyra.core.datascience_warnings import (
    CategoricalPlotWarning,
)

import lyra.semantics.utilities as utilities
import warnings


class SeabornDatascienceTypeSemantics:

    def set_seaborn_library_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        state.result = {DatascienceTypeLattice.Status.NoneRet}
        return state

    def lineplot_call_semantics(
        self, stmt: Call, state: DatascienceTypeState, interpreter: ForwardInterpreter
    ) -> DatascienceTypeState:
        data = None

        # Extract the data argument (DataFrame)
        for arg in stmt.arguments:
            if isinstance(arg, Keyword) and arg.name == "data":
                # Find the DataFrame being used
                for v in state.variables:
                    if utilities.is_DataFrame(state, v):
                        data = v
                        break

        # If no keyword data argument, check for positional usage
        if data is None:
            for arg in stmt.arguments:
                if isinstance(arg, VariableAccess):
                    tmp_arg = arg.variable
                elif isinstance(arg, VariableIdentifier):
                    tmp_arg = arg
                else:
                    continue

                if tmp_arg and utilities.is_DataFrame(state, tmp_arg):
                    data = tmp_arg
                    break

        # Check x and y arguments for categorical data
        for arg in stmt.arguments:
            arg_to_print = arg if not isinstance(arg, DatascienceTypeLattice.Status) else stmt

            if isinstance(arg, Keyword) and arg.name in ["x", "y"]:
                # Check if the argument references a column in the data DataFrame
                possible_col_name = arg.value

                if data and data in state.subscriptions:
                    for sub in state.subscriptions[data]:
                        if sub.key.val == possible_col_name:
                            # Check if the column is categorical or string
                            if utilities.is_CatSeries(state, sub):
                                warnings.warn(
                                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg.name}='{possible_col_name}' is a categorical Series, lineplot is better suited for numeric data.",
                                    category=CategoricalPlotWarning,
                                    stacklevel=2,
                                )
                            elif utilities.is_StringSeries(state, sub):
                                warnings.warn(
                                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg.name}='{possible_col_name}' is a string Series, lineplot is better suited for numeric data.",
                                    category=CategoricalPlotWarning,
                                    stacklevel=2,
                                )
                            elif utilities.is_Series(state, sub) and not utilities.is_NumericSeries(state, sub):
                                if interpreter.warning_level == "potential":
                                    warnings.warn(
                                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg.name}='{possible_col_name}' could contain categorical data, lineplot is better suited for numeric data.",
                                        category=CategoricalPlotWarning,
                                        stacklevel=2,
                                    )
                            break
                elif interpreter.warning_level == "potential":
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, lineplot is better suited for numeric data.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )

            # Direct checks for various data types passed as arguments
            if utilities.is_StringArray(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string array, lineplot is better suited for numeric data.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_StringList(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string list, lineplot is better suited for numeric data.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_CatSeries(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a categorical Series, lineplot is better suited for numeric data.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif utilities.is_StringSeries(state, arg):
                warnings.warn(
                    f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string Series, lineplot is better suited for numeric data.",
                    category=CategoricalPlotWarning,
                    stacklevel=2,
                )
            elif isinstance(arg, SubscriptionAccess):
                # Handle subscriptions like df['column']
                if utilities.is_CatSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a categorical Series, lineplot is better suited for numeric data.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
                elif utilities.is_StringSeries(state, arg):
                    warnings.warn(
                        f"Warning [plausible]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} is a string Series, lineplot is better suited for numeric data.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
                elif utilities.is_Series(state, arg) and not utilities.is_NumericSeries(state, arg):
                    if interpreter.warning_level == "potential":
                        warnings.warn(
                            f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, lineplot is better suited for numeric data.",
                            category=CategoricalPlotWarning,
                            stacklevel=2,
                        )
            elif utilities.is_Series(state, arg) and not utilities.is_NumericSeries(state, arg):
                if interpreter.warning_level == "potential":
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, lineplot is better suited for numeric data.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )
            elif (utilities.is_Array(state, arg) or utilities.is_Top(state, arg)) and not utilities.is_NumericArray(state, arg):
                if interpreter.warning_level == "potential":
                    warnings.warn(
                        f"Warning [potential]: in {stmt} @ line {stmt.pp.line} -> {arg_to_print} could contain categorical data, lineplot is better suited for numeric data.",
                        category=CategoricalPlotWarning,
                        stacklevel=2,
                    )

        state.result = {DatascienceTypeLattice.Status.Plot}
        return state
