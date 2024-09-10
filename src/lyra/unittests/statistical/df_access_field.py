import  pandas as pd
# STATE: a -> Top; b -> Top; c -> Top; df -> Top
df = pd.read_csv("...")
# STATE: a -> Top; b -> Top; c -> Top; df -> DataFrame
a = df.shape
# STATE: a -> Top; b -> Top; c -> Top; df -> DataFrame
b = df.calories
# STATE: a -> Top; b -> Series; c -> Top; df -> DataFrame
c = df.dtypes
# FINAL: a -> Top; b -> Series; c -> Series; df -> DataFrame