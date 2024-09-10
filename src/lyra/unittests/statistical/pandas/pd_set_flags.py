import pandas as pd
# STATE: df -> Top; df2 -> Top; s1 -> Top; s2 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df2 -> Top; s1 -> Top; s2 -> Top
df2 = df.set_flags()
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Top; s2 -> Top
s1 = df["b"]
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Top
s2 = s1.set_flags()
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series
