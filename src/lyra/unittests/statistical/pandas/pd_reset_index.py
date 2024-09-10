import pandas as pd

# STATE: df -> Top; none -> Top; s -> Top
df = pd.DataFrame([[1,2], [3,4]])
# STATE: df -> DataFrame; none -> Top; s -> Top
df = df.reset_index()
# STATE: df -> DataFrame; none -> Top; s -> Top
none = df.reset_index(inplace=True)
# STATE: df -> DataFrame; none -> NoneRet; s -> Top

s = pd.Series([1,2])
# STATE: df -> DataFrame; none -> NoneRet; s -> Series
df = s.reset_index()
# STATE: df -> DataFrame; none -> NoneRet; s -> Series
s = s.reset_index(drop=True)
# STATE: df -> DataFrame; none -> NoneRet; s -> Series
none = s.reset_index(drop=True, inplace=True)
# FINAL: df -> DataFrame; none -> NoneRet; s -> Series
