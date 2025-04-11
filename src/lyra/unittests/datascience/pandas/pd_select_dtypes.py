import pandas as pd
# STATE: df1 -> Top; df2 -> Top
df1 = pd.read_csv("...")
# STATE: df1 -> DataFrame; df2 -> Top
df2 = df1.select_dtypes(include='col')
# FINAL: df1 -> DataFrame; df2 -> DataFrame
