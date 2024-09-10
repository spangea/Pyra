import pandas as pd
# STATE: data -> Top; df -> Top; l -> Top; s1 -> Top; z1 -> Top; z2 -> Top
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; l -> Top; s1 -> Top; z1 -> Top; z2 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; l -> Top; s1 -> Top; z1 -> Top; z2 -> Top
s1 = df.sum()
# STATE: data -> Dict; df -> DataFrame; l -> Top; s1 -> Series; z1 -> Top; z2 -> Top
z1 = df["points"].sum()
# STATE: data -> Dict; df -> DataFrame; l -> Top; s1 -> Series; z1 -> Numeric; z2 -> Top
l = [1,2,3]
# STATE: data -> Dict; df -> DataFrame; l -> NumericList; s1 -> Series; z1 -> Numeric; z2 -> Top
z2 = l.sum()
# FINAL: data -> Dict; df -> DataFrame; l -> NumericList; s1 -> Series; z1 -> Numeric; z2 -> Numeric