import pandas as pd
# STATE: data -> Top; df -> Top; df1 -> Top; s2 -> Top; v1 -> Top; v2 -> Top
data = {
   0: [100, 120, 114],
   1: [350, 340, 402]
}
# STATE: data -> Dict; df -> Top; df1 -> Top; s2 -> Top; v1 -> Top; v2 -> Top
df = pd.DataFrame(data)
# STATE: data -> Dict; df -> DataFrame; df1 -> Top; s2 -> Top; v1 -> Top; v2 -> Top
df1 = df.loc[[0,1]]
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; s2 -> Top; v1 -> Top; v2 -> Top
s2 = df.loc[0]
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; s2 -> Series; v1 -> Top; v2 -> Top
df.loc[1,0] = 11    # Should raise a warning
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; df[(1, 0)] -> Numeric; s2 -> Series; v1 -> Top; v2 -> Top
v1= df.loc[1,0]
# STATE: data -> Dict; df -> DataFrame; df1 -> DataFrame; df[(1, 0)] -> Numeric; s2 -> Series; v1 -> Scalar; v2 -> Top
v2 = s2.loc[0]
# FINAL: data -> Dict; df -> DataFrame; df1 -> DataFrame; df[(1, 0)] -> Numeric; s2 -> Series; v1 -> Scalar; v2 -> Scalar

