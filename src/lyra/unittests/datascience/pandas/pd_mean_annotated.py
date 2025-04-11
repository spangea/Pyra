import pandas as pd
# STATE: df -> DataFrame; s -> Top; x -> Top; y -> Top; z -> Top
df : pd.DataFrame = pd.read_csv("...")
# STATE: df -> DataFrame; s -> Top; x -> Top; y -> Top; z -> Top
x = df.mean()
# STATE: df -> DataFrame; s -> Top; x -> Series; y -> Top; z -> Top
s = df["calories"]
# STATE: df -> DataFrame; s -> Series; x -> Series; y -> Top; z -> Top
y = s.mean()
# STATE: df -> DataFrame; s -> Series; x -> Series; y -> Numeric; z -> Top
z = df["calories"].mean()
# FINAL: df -> DataFrame; s -> Series; x -> Series; y -> Numeric; z -> Numeric