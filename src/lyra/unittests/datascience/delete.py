# STATE: a -> Top; b -> Top; c -> Top
a = 5
# STATE: a -> Numeric; b -> Top; c -> Top
b = 6
# STATE: a -> Numeric; b -> Numeric; c -> Top
c = 7
# STATE: a -> Numeric; b -> Numeric; c -> Numeric
del a, b
# STATE: c -> Numeric
a = "string"
# FINAL: a -> String; c -> Numeric
