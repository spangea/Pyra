import pandas as pd
# STATE: df -> DataFrame; rs -> Top
df : pd.DataFrame = pd.read_csv("...")
# STATE: df -> DataFrame; rs -> Top
rs = df['a'] / df['b']
# FINAL: df -> DataFrame; rs -> RatioSeries

