import pandas as pd
# STATE: df -> Top; l -> Top; s -> Top; s1 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; l -> Top; s -> Top; s1 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
s = df.count()
# STATE: df -> DataFrame; l -> Top; s -> Series; s1 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
s1 = df["b"]
# STATE: df -> DataFrame; l -> Top; s -> Series; s1 -> Series; z1 -> Top; z2 -> Top; z3 -> Top
z1 = df["a"].count()
# STATE: df -> DataFrame; l -> Top; s -> Series; s1 -> Series; z1 -> Numeric; z2 -> Top; z3 -> Top
z2 = s1.count()
# STATE: df -> DataFrame; l -> Top; s -> Series; s1 -> Series; z1 -> Numeric; z2 -> Numeric; z3 -> Top
l = [1,2,3]
# STATE: df -> DataFrame; l -> NumericList; s -> Series; s1 -> Series; z1 -> Numeric; z2 -> Numeric; z3 -> Top
z3 = l.count(1)
# FINAL: df -> DataFrame; l -> NumericList; s -> Series; s1 -> Series; z1 -> Numeric; z2 -> Numeric; z3 -> Numeric

