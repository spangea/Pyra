import numpy as np
# STATE: a -> Top; b -> Top; c -> Top; d -> Top
a = np.arange(True, False)
# STATE: a -> Array; b -> Top; c -> Top; d -> Top
b = np.arange(1, 3, dtype=float)
# STATE: a -> Array; b -> NumericArray; c -> Top; d -> Top
c = np.arange(1, 3, dtype=bool)
# STATE: a -> Array; b -> NumericArray; c -> BoolArray; d -> Top
d = np.arange(6, 9, 1)
# FINAL: a -> Array; b -> NumericArray; c -> BoolArray; d -> NumericArray