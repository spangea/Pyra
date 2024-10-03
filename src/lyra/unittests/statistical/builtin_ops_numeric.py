# STATE: a -> Top; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top
a = 1
# STATE: a -> Numeric; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top
b = 2
# STATE: a -> Numeric; b -> Numeric; c -> Top; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top
c = a - b
# STATE: a -> Numeric; b -> Numeric; c -> Numeric; d -> Top; e -> Top; f -> Top; g -> Top; h -> Top
d = a * b
# STATE: a -> Numeric; b -> Numeric; c -> Numeric; d -> Numeric; e -> Top; f -> Top; g -> Top; h -> Top
e = a - b
# STATE: a -> Numeric; b -> Numeric; c -> Numeric; d -> Numeric; e -> Numeric; f -> Top; g -> Top; h -> Top
f = a / b
# STATE: a -> Numeric; b -> Numeric; c -> Numeric; d -> Numeric; e -> Numeric; f -> Numeric; g -> Top; h -> Top
g = a % b
# STATE: a -> Numeric; b -> Numeric; c -> Numeric; d -> Numeric; e -> Numeric; f -> Numeric; g -> Numeric; h -> Top
h = -a
# FINAL: a -> Numeric; b -> Numeric; c -> Numeric; d -> Numeric; e -> Numeric; f -> Numeric; g -> Numeric; h -> Numeric
