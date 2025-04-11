import pandas as pd
# STATE: df -> Top; df2 -> Top; df3 -> Top; s1 -> Top; s2 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df2 -> Top; df3 -> Top; s1 -> Top; s2 -> Top
df2 =  pd.read_csv("...")
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> Top; s1 -> Top; s2 -> Top
s1 = df["b"]
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> Top; s1 -> Series; s2 -> Top
s2 = df["a"]
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> Top; s1 -> Series; s2 -> Series
df3 = pd.crosstab(s1, s2)
# FINAL: df -> DataFrame; df2 -> DataFrame; df3 -> DataFrame; s1 -> Series; s2 -> Series
