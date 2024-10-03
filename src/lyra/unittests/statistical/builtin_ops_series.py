import  pandas as pd
# STATE: a -> Top; b -> Top; c -> Top; d -> Top; df -> Top; e -> Top; s1 -> Top; s2 -> Top; z -> Top
df = pd.read_csv("...")
# STATE: a -> Top; b -> Top; c -> Top; d -> Top; df -> DataFrame; e -> Top; s1 -> Top; s2 -> Top; z -> Top
s1 = df['a']
# STATE: a -> Top; b -> Top; c -> Top; d -> Top; df -> DataFrame; e -> Top; s1 -> Series; s2 -> Top; z -> Top
s2 = df['b']
# STATE: a -> Top; b -> Top; c -> Top; d -> Top; df -> DataFrame; e -> Top; s1 -> Series; s2 -> Series; z -> Top
a = s1 - s2
# STATE: a -> Series; b -> Top; c -> Top; d -> Top; df -> DataFrame; e -> Top; s1 -> Series; s2 -> Series; z -> Top
b = s1 + s2
# STATE: a -> Series; b -> Series; c -> Top; d -> Top; df -> DataFrame; e -> Top; s1 -> Series; s2 -> Series; z -> Top
c = s1 * s2
# STATE: a -> Series; b -> Series; c -> Series; d -> Top; df -> DataFrame; e -> Top; s1 -> Series; s2 -> Series; z -> Top
d = s1 / s2
# STATE: a -> Series; b -> Series; c -> Series; d -> RatioSeries; df -> DataFrame; e -> Top; s1 -> Series; s2 -> Series; z -> Top
e = s1 % s2
# STATE: a -> Series; b -> Series; c -> Series; d -> RatioSeries; df -> DataFrame; e -> Series; s1 -> Series; s2 -> Series; z -> Top
z = -a
# FINAL: a -> Series; b -> Series; c -> Series; d -> RatioSeries; df -> DataFrame; e -> Series; s1 -> Series; s2 -> Series; z -> Series
