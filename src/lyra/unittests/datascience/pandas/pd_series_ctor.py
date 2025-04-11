import pandas as pd
# STATE: data -> Top; s -> Top
data = {"a" : [1, 2], "b" : [3,4]}
# STATE: data -> Dict; s -> Top
s = pd.Series(data)
# FINAL: data -> Dict; s -> Series
