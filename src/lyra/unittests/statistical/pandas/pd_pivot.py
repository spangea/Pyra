import pandas as pd
# STATE: df -> Top; df1 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df1 -> Top
df1 = df.pivot()
# FINAL: df -> DataFrame; df1 -> DataFrame