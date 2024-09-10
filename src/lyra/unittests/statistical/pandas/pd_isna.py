import pandas as pd
# STATE: df -> Top; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
df2 = df.isna()
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Top; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
s1 = df["b"]
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
s2 = df["a"].isna()
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
s3 = s1.isna()
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> Top; z2 -> Top; z3 -> Top
z1 = pd.isna(df)
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Top; z3 -> Top
z2 = pd.isna(s3)
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Series; z3 -> Top
z3 =  pd.isna("")
# FINAL: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Series; z3 -> Boolean
