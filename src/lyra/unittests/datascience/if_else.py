import pandas as pd
# STATE: l -> Top
l = [1]
# STATE: l -> NumericList
if 1 > 5:
    l = [1, 2, 3]
    # STATE: l -> NumericList
else:
    l = ["a", "b", "c"]
    # STATE: l -> StringList
# FINAL: l -> List
