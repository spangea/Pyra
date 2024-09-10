# STATE: w -> Top; x -> Top; y -> Top; z -> Top
x = 1
# STATE: w -> Top; x -> Numeric; y -> Top; z -> Top
y = 2
# STATE: w -> Top; x -> Numeric; y -> Numeric; z -> Top
x = lambda a, b, c : a + b + c
# STATE: w -> Top; x -> Top; y -> Numeric; z -> Top
y = x
# STATE: w -> Top; x -> Top; y -> Top; z -> Top
z = x(1, 2, 3)
# STATE: w -> Top; x -> Top; y -> Top; z -> Top
w = y(1, 2, 3)
# STATE: w -> Top; x -> Top; y -> Top; z -> Top
