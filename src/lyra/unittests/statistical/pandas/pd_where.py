import pandas as pd
# STATE: df1 -> Top; df2 -> Top; s -> Top; s1 -> Top; tnone -> Top
df1 = pd.read_csv("...")
# STATE: df1 -> DataFrame; df2 -> Top; s -> Top; s1 -> Top; tnone -> Top
df2 = df1.where(df1["a"] > df1["b"])
# STATE: df1 -> DataFrame; df2 -> DataFrame; s -> Top; s1 -> Top; tnone -> Top
s = pd.Series(range(5))
# STATE: df1 -> DataFrame; df2 -> DataFrame; s -> Series; s1 -> Top; tnone -> Top
s1 = s.where(s > 0)
# STATE: df1 -> DataFrame; df2 -> DataFrame; s -> Series; s1 -> Series; tnone -> Top
tnone = s.where(s > 0, inplace=True)
# STATE: df1 -> DataFrame; df2 -> DataFrame; s -> Series; s1 -> Series; tnone -> NoneRet
tnone = df1.where(df1["a"] > df1["b"], inplace=True)
# FINAL: df1 -> DataFrame; df2 -> DataFrame; s -> Series; s1 -> Series; tnone -> NoneRet
