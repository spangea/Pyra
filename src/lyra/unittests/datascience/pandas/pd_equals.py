import pandas as pd
# STATE: data -> Top; df -> Top; z1 -> Top; z3 -> Top
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; z1 -> Top; z3 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; z1 -> Top; z3 -> Top
z1 = df.equals(df)
# STATE: data -> Dict; df -> DataFrame; z1 -> Boolean; z3 -> Top
z3 = df["points"].equals(df["total"])
# FINAL: data -> Dict; df -> DataFrame; z1 -> Boolean; z3 -> Boolean
