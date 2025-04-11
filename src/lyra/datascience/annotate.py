# Given the results of the previously computed analysis,
# create a new file with the type annotations for the
# inferred abstract data types to be used in the
# dataframe usage analysis.

from itertools import zip_longest
from lyra.core.cfg import Node, Edge
import re

def get_vars(results):
    # Results have shape 'v1 -> t1; v2 -> t2; ...; vn -> tn
    # Get the variables and their inferred types
    try:
        results = results.split(";")
        results = [result.split("->") for result in results]
        results = [(var.strip(), inferred_type.strip()) for var, inferred_type in results]
    except:
        # Trying to analyze a statement
        results = []
    return results

def keep_only_dataframes(results):
    # For the inferred types, keep only the variables that are DataFrames
    # For the other ones, replace the inferred type with None
    results = [(var, inferred_type) if "DataFrame" in inferred_type else (var, None) for var, inferred_type in results]
    return results

def annotate(results, python_file):

    df_tracked_vars = set() # Set of variables for which a DataFrame type has been inferred

    # Visit all the nodes in the control flow graph and keep track of the variables
    # for which a DataFrame type has been inferred
    # Algorithm taken from src/lyra/engine/result.py
    # **** START VISITING NODES ****
    visited, pending = set(), list()
    pending.append(results.cfgs[''].in_node)
    while pending:
        current = pending.pop()
        if current not in visited:
            if isinstance(current, Node):
                states = next(iter(results.get_node_result(current).values()))
                node = [item for items in zip_longest(states, current.stmts)
                        for item in items if item is not None]

                # Get the inferred variables and their types
                inferred_vars = []
                for res in node:
                    inferred_vars.extend(keep_only_dataframes(get_vars(str(res))))
                inferred_vars = [(var, inferred_type) for var, inferred_type in inferred_vars if inferred_type is not None]
                df_tracked_vars.update(inferred_vars)

                for edge in results.cfgs[''].out_edges(current):
                        if edge not in visited:
                            pending.append(edge)
            elif isinstance(current, Edge):
                if current.target not in visited:
                    pending.append(current.target)
            visited.add(current)
    # **** END VISITING NODES ****


    df_tracked_vars = dict(df_tracked_vars)
    # Working on copy of the actual python file
    # annotate the variables for which a DataFrame type has been inferred
    # by adding pd.DataFrame only the very first time they are assigned in the code
    annotated_file = python_file.replace(".py", "_annotated.py")
    with open(python_file, "r") as f:
        with open(annotated_file, "w") as g:
            for line in f:
                if not line.strip().startswith("#"):
                    for var, inferred_type in df_tracked_vars.items():
                        if inferred_type is not None:
                            if re.search(rf"\b{var}\b\s*=", line):
                                line = re.sub(rf"\b{var}\b", f"{var}: pd.DataFrame", line)
                                df_tracked_vars[var] = None
                g.write(line)


