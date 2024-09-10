import pandas as pd
# STATE: df -> Top; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top
df2 = df.rename_axis("abc")
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Top; s2 -> Top; s3 -> Top
s1 = df["b"]
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Top; s3 -> Top
s2 = df["a"].rename_axis("abc")
# STATE: df -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Top
s3 = s1.rename_axis("abc")
s1.rename_axis("abc",inplace=True)
df.rename_axis("abc",inplace=True)
df["a"].rename_axis("abc",inplace=True)
# FINAL: df -> DataFrame; df2 -> DataFrame; df["a"] -> Series; s1 -> Series; s2 -> Series; s3 -> Series
