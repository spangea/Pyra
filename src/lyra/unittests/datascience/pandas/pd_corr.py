import pandas as pd
# STATE: data -> Top; df -> Top; df1 -> Top; z1 -> Top
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; df1 -> Top; z1 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; df1 -> Top; z1 -> Top
df1 = df.corr()
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; z1 -> Top
z1 = df["points"].corr(df["points"])
# FINAL: data -> Dict; df -> DataFrame; df1 -> DataFrame; z1 -> Numeric
