import pandas as pd
# STATE: data -> Top; df -> Top; df1 -> Top; s1 -> Top
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; df1 -> Top; s1 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; df1 -> Top; s1 -> Top
s1 = df["total"]
# STATE: data -> Dict; df -> DataFrame; df1 -> Top; s1 -> Series
df1 = df[["points"]]
# FINAL: data -> Dict; df -> DataFrame; df1 -> DataFrame; s1 -> Series
