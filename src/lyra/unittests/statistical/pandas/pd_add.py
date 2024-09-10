import pandas as pd
# STATE: data -> Top; df -> Top; df1 -> Top; s1 -> Top; set1 -> Top
data = {
  "points": [100, 120, 114],
  "total": [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; df1 -> Top; s1 -> Top; set1 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; df1 -> Top; s1 -> Top; set1 -> Top
df1 = df.add(15)
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; s1 -> Top; set1 -> Top
s1 = df["points"].add(1)
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; s1 -> Series; set1 -> Top
set1 = {"a"}
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; s1 -> Series; set1 -> Set
set1.add("b")
# FINAL: data -> Dict; df -> DataFrame; df1 -> DataFrame; s1 -> Series; set1 -> Set
