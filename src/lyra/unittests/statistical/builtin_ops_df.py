import  pandas as pd
# STATE: a -> Top; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top; i -> Top; l -> Top
a = pd.read_csv("...")
# STATE: a -> DataFrame; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top; i -> Top; l -> Top
b = pd.read_csv("...")
# STATE: a -> DataFrame; b -> DataFrame; c -> Top; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top; i -> Top; l -> Top
c = a - b
# STATE: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top; i -> Top; l -> Top
d = a * b
# STATE: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> DataFrame; e -> Top; f -> Top; g -> Top; h -> Top; i -> Top; l -> Top
e = a - b
# STATE: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> DataFrame; e -> DataFrame; f -> Top; g -> Top; h -> Top; i -> Top; l -> Top
f = a / b
# STATE: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> DataFrame; e -> DataFrame; f -> DataFrame; g -> Top; h -> Top; i -> Top; l -> Top
g = a % b
# STATE: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> DataFrame; e -> DataFrame; f -> DataFrame; g -> DataFrame; h -> Top; i -> Top; l -> Top
h = a * 5
# STATE: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> DataFrame; e -> DataFrame; f -> DataFrame; g -> DataFrame; h -> DataFrame; i -> Top; l -> Top
i = 5 * a
# STATE: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> DataFrame; e -> DataFrame; f -> DataFrame; g -> DataFrame; h -> DataFrame; i -> DataFrame; l -> Top
l = -a
# FINAL: a -> DataFrame; b -> DataFrame; c -> DataFrame; d -> DataFrame; e -> DataFrame; f -> DataFrame; g -> DataFrame; h -> DataFrame; i -> DataFrame; l -> DataFrame
