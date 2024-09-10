import pandas as pd
# STATE: df -> Top; rs -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; rs -> Top
rs = df['a'] / df['b']
# FINAL: df -> DataFrame; rs -> RatioSeries

