import pandas as pd
# STATE: df -> Top; s -> Top; s1 -> Top; z1 -> Top; z2 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; s -> Top; s1 -> Top; z1 -> Top; z2 -> Top
s = df.memory_usage()
# STATE: df -> DataFrame; s -> Series; s1 -> Top; z1 -> Top; z2 -> Top
s1 = df["b"]
# STATE: df -> DataFrame; s -> Series; s1 -> Series; z1 -> Top; z2 -> Top
z1 = df["a"].memory_usage()
# STATE: df -> DataFrame; s -> Series; s1 -> Series; z1 -> Numeric; z2 -> Top
z2 = s1.memory_usage()
# FINAL: df -> DataFrame; s -> Series; s1 -> Series; z1 -> Numeric; z2 -> Numeric
