import pandas as pd
# STATE: absolute_number -> Top; data -> Top; df -> Top; df1 -> Top; number -> Top; s1 -> Top
number = -20
# STATE: absolute_number -> Top; data -> Top; df -> Top; df1 -> Top; number -> Numeric; s1 -> Top
absolute_number = abs(number)
# STATE: absolute_number -> Numeric; data -> Top; df -> Top; df1 -> Top; number -> Numeric; s1 -> Top
data = [[-50, 40, 30], [-1, 2, -2]]
# STATE: absolute_number -> Numeric; data -> List; df -> Top; df1 -> Top; number -> Numeric; s1 -> Top
df = pd.DataFrame(data)
# STATE: absolute_number -> Numeric; data -> List; df -> DataFrame; df1 -> Top; number -> Numeric; s1 -> Top
df1 = df.abs()
# STATE: absolute_number -> Numeric; data -> List; df -> DataFrame; df1 -> DataFrame; number -> Numeric; s1 -> Top
s1 = df[0].abs()
# FINAL: absolute_number -> Numeric; data -> List; df -> DataFrame; df1 -> DataFrame; number -> Numeric; s1 -> Series
