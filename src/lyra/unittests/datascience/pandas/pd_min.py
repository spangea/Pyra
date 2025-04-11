import pandas as pd
# STATE: df -> Top; s -> Top; x -> Top; y -> Top; z -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; s -> Top; x -> Top; y -> Top; z -> Top
x = df.min()
# STATE: df -> DataFrame; s -> Top; x -> Series; y -> Top; z -> Top
s = df["calories"]
# STATE: df -> DataFrame; s -> Series; x -> Series; y -> Top; z -> Top
y = s.min()
# STATE: df -> DataFrame; s -> Series; x -> Series; y -> Numeric; z -> Top
z = df["calories"].min()
# FINAL: df -> DataFrame; s -> Series; x -> Series; y -> Numeric; z -> Numeric