import pandas as pd
# STATE: data -> Top; df -> Top; s1 -> Top; z1 -> Top
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; s1 -> Top; z1 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; s1 -> Top; z1 -> Top
s1 = df.prod()
# STATE: data -> Dict; df -> DataFrame; s1 -> Series; z1 -> Top
z1 = df["points"].prod()
# FINAL: data -> Dict; df -> DataFrame; s1 -> Series; z1 -> Numeric