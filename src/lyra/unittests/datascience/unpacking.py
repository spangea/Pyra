import numpy as np

# STATE: a -> Top; b -> Top; c -> Top; n -> Top; numarr -> Top
c = 2
# STATE: a -> Top; b -> Top; c -> Numeric; n -> Top; numarr -> Top
a, b = (1,2)
# STATE: a -> Numeric; b -> Numeric; c -> Numeric; n -> Top; numarr -> Top

numarr, n = np.linspace(1,10, retstep=True)
# FINAL: a -> Numeric; b -> Numeric; c -> Numeric; n -> Numeric; numarr -> NumericArray
