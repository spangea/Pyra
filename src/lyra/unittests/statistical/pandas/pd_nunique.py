import pandas as pd
# STATE: df -> Top; z1 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; z1 -> Top
z1 = df.nunique()
# FINAL: df -> DataFrame; z1 -> Numeric