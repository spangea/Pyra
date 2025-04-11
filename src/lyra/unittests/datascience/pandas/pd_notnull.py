import pandas as pd
import numpy as np
# STATE: array -> Top; df -> Top; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top; z4 -> Top
df = pd.read_csv("...")
# STATE: array -> Top; df -> DataFrame; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top; z4 -> Top
df2 = df.notnull()
# STATE: array -> Top; df -> DataFrame; df2 -> DataFrame; s1 -> Top; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top; z4 -> Top
s1 = df["b"]
# STATE: array -> Top; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Top; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top; z4 -> Top
s2 = df["a"].notnull()
# STATE: array -> Top; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Top; z1 -> Top; z2 -> Top; z3 -> Top; z4 -> Top
s3 = s1.notnull()
# STATE: array -> Top; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> Top; z2 -> Top; z3 -> Top; z4 -> Top
z1 = pd.notnull(df)
# STATE: array -> Top; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Top; z3 -> Top; z4 -> Top
z2 = pd.notnull(s3)
# STATE: array -> Top; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Series; z3 -> Top; z4 -> Top
z3 = pd.notnull("")
# STATE: array -> Top; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Series; z3 -> Boolean; z4 -> Top
array = np.array([1, 2, 3, 4, 5, 6])
# STATE: array -> NumericArray; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Series; z3 -> Boolean; z4 -> Top
z4 = pd.notnull(array)
# FINAL: array -> NumericArray; df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series; z1 -> DataFrame; z2 -> Series; z3 -> Boolean; z4 -> BoolArray
