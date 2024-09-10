import pandas as pd
# STATE: data -> Top; df -> Top; s1 -> Top; s3 -> Top
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; s1 -> Top; s3 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; s1 -> Top; s3 -> Top
s1 = df.duplicated()
# STATE: data -> Dict; df -> DataFrame; s1 -> BoolSeries; s3 -> Top
s3 = df["points"].duplicated()
# FINAL: data -> Dict; df -> DataFrame; s1 -> BoolSeries; s3 -> BoolSeries
