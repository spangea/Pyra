import pandas as pd
# STATE: a -> Top; b -> Top; c -> Top; d -> Top; df -> Top; e -> Top
df = pd.DataFrame()
# STATE: a -> Top; b -> Top; c -> Top; d -> Top; df -> DataFrame; e -> Top
a = df['rate'].unique()
# STATE: a -> Array; b -> Top; c -> Top; d -> Top; df -> DataFrame; e -> Top
b = df['a'] / df['b']
# STATE: a -> Array; b -> RatioSeries; c -> Top; d -> Top; df -> DataFrame; e -> Top
c = b.unique()
# STATE: a -> Array; b -> RatioSeries; c -> NumericArray; d -> Top; df -> DataFrame; e -> Top
d = df.duplicated()
# STATE: a -> Array; b -> RatioSeries; c -> NumericArray; d -> BoolSeries; df -> DataFrame; e -> Top
e = d.unique()
# FINAL: a -> Array; b -> RatioSeries; c -> NumericArray; d -> BoolSeries; df -> DataFrame; e -> BoolArray

