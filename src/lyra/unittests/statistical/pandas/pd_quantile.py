import pandas as pd
# STATE: df -> Top; df2 -> Top; df3 -> Top; n -> Top; n2 -> Top; s -> Top; s2 -> Top; s3 -> Top; s4 -> Top
df = pd.read_csv('...')
# STATE: df -> DataFrame; df2 -> Top; df3 -> Top; n -> Top; n2 -> Top; s -> Top; s2 -> Top; s3 -> Top; s4 -> Top
s = df.quantile()
# STATE: df -> DataFrame; df2 -> Top; df3 -> Top; n -> Top; n2 -> Top; s -> Series; s2 -> Top; s3 -> Top; s4 -> Top
s2 = df.quantile(1)
# STATE: df -> DataFrame; df2 -> Top; df3 -> Top; n -> Top; n2 -> Top; s -> Series; s2 -> Series; s3 -> Top; s4 -> Top
df2 = df.quantile([1])
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> Top; n -> Top; n2 -> Top; s -> Series; s2 -> Series; s3 -> Top; s4 -> Top
df3 = df.quantile(s)
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> DataFrame; n -> Top; n2 -> Top; s -> Series; s2 -> Series; s3 -> Top; s4 -> Top
s3 = s.quantile(s2)
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> DataFrame; n -> Top; n2 -> Top; s -> Series; s2 -> Series; s3 -> Series; s4 -> Top
s4 = s.quantile([1])
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> DataFrame; n -> Top; n2 -> Top; s -> Series; s2 -> Series; s3 -> Series; s4 -> Series
n = s.quantile(1)
# STATE: df -> DataFrame; df2 -> DataFrame; df3 -> DataFrame; n -> Numeric; n2 -> Top; s -> Series; s2 -> Series; s3 -> Series; s4 -> Series
n2 = s.quantile()
# FINAL: df -> DataFrame; df2 -> DataFrame; df3 -> DataFrame; n -> Numeric; n2 -> Numeric; s -> Series; s2 -> Series; s3 -> Series; s4 -> Series
