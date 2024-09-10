import pandas as pd
# STATE: df1 -> Top; s -> Top
df1 = pd.read_csv("...")
# STATE: df1 -> DataFrame; s -> Top
s = df1.value_counts(include='col')
# FINAL: df1 -> DataFrame; s -> Series
