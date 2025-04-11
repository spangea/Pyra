import pandas as pd
# STATE: df -> Top; df1 -> Top; df2 -> Top; s1 -> Top; s2 -> Top; s3 -> Top
s1 = pd.Series(['a', 'b'])
# STATE: df -> Top; df1 -> Top; df2 -> Top; s1 -> Series; s2 -> Top; s3 -> Top
s2 = pd.Series(['c', 'd'])
# STATE: df -> Top; df1 -> Top; df2 -> Top; s1 -> Series; s2 -> Series; s3 -> Top
s3 = pd.concat([s1, s2])
# STATE: df -> Top; df1 -> Top; df2 -> Top; s1 -> Series; s2 -> Series; s3 -> Series
df = pd.read_csv("...")
# STATE: df -> DataFrame; df1 -> Top; df2 -> Top; s1 -> Series; s2 -> Series; s3 -> Series
df1 = pd.concat([s1, df])
# STATE: df -> DataFrame; df1 -> DataFrame; df2 -> Top; s1 -> Series; s2 -> Series; s3 -> Series
df2 = pd.concat([s1, s2], axis=1)
# FINAL: df -> DataFrame; df1 -> DataFrame; df2 -> DataFrame; s1 -> Series; s2 -> Series; s3 -> Series

