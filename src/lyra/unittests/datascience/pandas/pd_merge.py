import pandas as pd
# STATE: df1 -> Top; df2 -> Top; df3 -> Top
df1 = pd.read_csv("...")
# STATE: df1 -> DataFrame; df2 -> Top; df3 -> Top
df2 = pd.read_csv("...")
# STATE: df1 -> DataFrame; df2 -> DataFrame; df3 -> Top
df3 = df1.merge(df2)
# FINAL: df1 -> DataFrame; df2 -> DataFrame; df3 -> DataFrame

