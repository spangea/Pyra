import pandas as pd
# STATE: df -> Top; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top
df2 = df.fillna(0)
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Top; s2 -> Top; s3 -> Top
s1 = df["b"]
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Top; s3 -> Top
s2 = df["a"].fillna(0)
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Top
s3 = s1.fillna(0)
s1.fillna(0,inplace=True)
df.fillna(0,inplace=True)
df["a"].fillna(0,inplace=True)
# FINAL: df -> DataFrame; df2 -> DataFrame; df["a"] -> Series; s1 -> Series; s2 -> Series; s3 -> Series
